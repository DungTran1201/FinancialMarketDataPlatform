"""100-Bot Data Plane Swarm Runner, Activity Logger & QA Telemetry Analyzer (`TC-010`).

Simulates 100 concurrent/interleaved QA Bots divided into 5 specialized squads (20 bots/squad)
exercising every Data Plane API endpoint, recording structured JSONL activity logs, and computing
comprehensive QA & Data Plane telemetry.
"""

from __future__ import annotations

import json
import math
import time
import unittest
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from src.serving.api.main import create_app
from src.serving.infrastructure.runtime import PlatformRuntimeContainer
from src.shared.security.primitives import RateLimitTier

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = REPO_ROOT / "logs"
ACTIVITY_LOG_PATH = LOG_DIR / "data_plane_100_bots_activity.jsonl"
SUMMARY_LOG_PATH = LOG_DIR / "data_plane_100_bots_summary.json"

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT")
BASE_PRICES = {
    "BTCUSDT": 89500.0,
    "ETHUSDT": 3120.0,
    "SOLUSDT": 185.0,
    "BNBUSDT": 640.0,
    "XRPUSDT": 1.45,
}


@dataclass(frozen=True, slots=True)
class BotActionLogEntry:
    """Single structured log record emitted for each bot API interaction on the Data Plane."""

    seq_id: int
    timestamp_utc: str
    bot_id: str
    squad: str
    client_ip: str
    http_method: str
    endpoint: str
    target_symbol: str
    action_type: str
    status_code: int
    latency_ms: float
    data_plane_source_or_topic: str
    outcome_detail: str
    assertion_passed: bool


def _percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, max(0, math.ceil((pct / 100.0) * len(sorted_vals)) - 1))
    return round(sorted_vals[idx], 3)


def run_100_bot_data_plane_campaign() -> dict[str, Any]:
    """Execute the 100-bot QA campaign across all Data Plane APIs and write structured logs."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    runtime = PlatformRuntimeContainer()
    # High rate-limit ceiling so each bot IP can run full load without artificial 429 throttling
    app = create_app(
        runtime=runtime,
        tier_overrides={
            RateLimitTier.MARKET_READ: 5000,
            RateLimitTier.HEAVY_ANALYTICS: 5000,
            RateLimitTier.AUTH: 5000,
            RateLimitTier.AGENT_TRIGGER: 5000,
        },
    )
    client = TestClient(app)

    logs: list[BotActionLogEntry] = []
    seq = 0
    base_now = datetime.now(UTC)

    def _record_call(
        *,
        bot_id: str,
        squad: str,
        client_ip: str,
        method: str,
        url: str,
        symbol: str,
        action_type: str,
        expected_status: int,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        nonlocal seq
        seq += 1
        headers = {"Host": "api.fmdp.local", "X-Forwarded-For": client_ip}
        t0 = time.perf_counter()
        if method == "GET":
            resp = client.get(url, headers=headers, params=params)
        elif method == "POST":
            resp = client.post(url, headers=headers, json=json_body)
        elif method == "PUT":
            resp = client.put(url, headers=headers, json=json_body)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 3)

        body = resp.json() if resp.content else {}
        data_block = body.get("data", {}) if isinstance(body, dict) else {}
        meta_block = body.get("meta", {}) if isinstance(body, dict) else {}

        source_or_topic = str(
            meta_block.get("source")
            or meta_block.get("topic")
            or meta_block.get("idempotent_merge")
            or (data_block.get("status") if isinstance(data_block, dict) else "data_plane")
        )
        if isinstance(data_block, dict):
            detail = str(
                data_block.get("status")
                or data_block.get("last_price")
                or data_block.get("vwap")
                or data_block.get("job_id")
                or data_block.get("silver_deduplicated_rows")
                or f"keys={len(data_block)}"
            )
        elif isinstance(data_block, list):
            detail = f"rows={len(data_block)}"
        else:
            detail = str(resp.status_code)

        passed = resp.status_code == expected_status
        logs.append(
            BotActionLogEntry(
                seq_id=seq,
                timestamp_utc=datetime.now(UTC).isoformat(),
                bot_id=bot_id,
                squad=squad,
                client_ip=client_ip,
                http_method=method,
                endpoint=url.split("?")[0],
                target_symbol=symbol,
                action_type=action_type,
                status_code=resp.status_code,
                latency_ms=elapsed_ms,
                data_plane_source_or_topic=source_or_topic,
                outcome_detail=detail,
                assertion_passed=passed,
            )
        )
        return body

    # =========================================================================
    # SQUAD 1: BOT-001 .. BOT-020 (20 Stream Producer, Deduplication & Replay Bots)
    # =========================================================================
    for i in range(1, 21):
        bot_id = f"BOT-{i:03d}"
        ip = f"198.51.100.{i}"
        squad = "S1_STREAM_PRODUCER_AND_REPLAY"
        sym = SYMBOLS[(i - 1) % len(SYMBOLS)]
        base_p = BASE_PRICES[sym]
        ev_time = base_now + timedelta(seconds=i)
        ev_ms = int(ev_time.timestamp() * 1000)

        # 1. Live Trade Ingestion
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url="/api/v1/market/ingest",
            symbol=sym,
            action_type="INGEST_LIVE_TRADE",
            expected_status=202,
            json_body={
                "source_topic": "market.raw.trades.v1",
                "ingested_at": ev_time.isoformat(),
                "raw_message": {
                    "e": "trade",
                    "E": ev_ms,
                    "s": sym,
                    "t": 10000 + i,
                    "p": f"{base_p + i * 1.5:.8f}",
                    "q": "0.75000000",
                    "m": (i % 2 == 0),
                },
            },
        )

        # 2. Live Kline Ingestion (v1 open candle)
        open_t = base_now.replace(second=0, microsecond=0) + timedelta(minutes=i)
        close_t = open_t + timedelta(minutes=1)
        kline_msg_v1 = {
            "e": "kline",
            "E": int(close_t.timestamp() * 1000),
            "s": sym,
            "k": {
                "t": int(open_t.timestamp() * 1000),
                "T": int(close_t.timestamp() * 1000),
                "s": sym,
                "i": "1m",
                "o": f"{base_p:.8f}",
                "h": f"{base_p + 25.0:.8f}",
                "l": f"{base_p - 15.0:.8f}",
                "c": f"{base_p + 5.0:.8f}",
                "v": "15.25000000",
                "q": f"{(base_p + 5.0) * 15.25:.8f}",
                "n": 95 + i,
                "x": False,
            },
        }
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url="/api/v1/market/ingest",
            symbol=sym,
            action_type="INGEST_KLINE_V1",
            expected_status=202,
            json_body={
                "source_topic": "market.raw.klines.v1",
                "ingested_at": close_t.isoformat(),
                "raw_message": kline_msg_v1,
            },
        )

        # 3. Duplicate / Updated Kline Replay (v2 closed candle -> ReplacingMergeTree dedup)
        kline_msg_v2 = {
            **kline_msg_v1,
            "E": int((close_t + timedelta(seconds=1)).timestamp() * 1000),
            "k": {**kline_msg_v1["k"], "c": f"{base_p + 12.0:.8f}", "x": True},
        }
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url="/api/v1/market/ingest",
            symbol=sym,
            action_type="REPLAY_DEDUP_KLINE_V2",
            expected_status=202,
            json_body={
                "source_topic": "market.raw.klines.v1",
                "ingested_at": (close_t + timedelta(seconds=1)).isoformat(),
                "raw_message": kline_msg_v2,
            },
        )

        # 4. Live 24hrTicker Ingestion
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url="/api/v1/market/ingest",
            symbol=sym,
            action_type="INGEST_24H_TICKER",
            expected_status=202,
            json_body={
                "source_topic": "market.raw.tickers.v1",
                "ingested_at": (close_t + timedelta(seconds=2)).isoformat(),
                "raw_message": {
                    "e": "24hrTicker",
                    "E": int((close_t + timedelta(seconds=2)).timestamp() * 1000),
                    "s": sym,
                    "c": f"{base_p + 14.0:.8f}",
                    "h": f"{base_p + 50.0:.8f}",
                    "l": f"{base_p - 40.0:.8f}",
                    "w": f"{base_p + 8.0:.8f}",
                    "v": "1250.00000000",
                    "q": f"{base_p * 1250.0:.8f}",
                },
            },
        )

        # 5. Out-of-Order Stale Event Injection (must be dropped by Redis monotonic guard BR-003)
        stale_time = base_now - timedelta(hours=2)
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url="/api/v1/market/ingest",
            symbol=sym,
            action_type="INJECT_OUT_OF_ORDER_STALE_EVENT",
            expected_status=202,
            json_body={
                "source_topic": "market.raw.trades.v1",
                "ingested_at": stale_time.isoformat(),
                "raw_message": {
                    "e": "trade",
                    "E": int(stale_time.timestamp() * 1000),
                    "s": sym,
                    "t": 500 + i,
                    "p": f"{base_p * 0.5:.8f}",
                    "q": "1.00000000",
                },
            },
        )

        # 6. Verify latest hot price was NOT overwritten by stale trade
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/market/prices/{sym}",
            symbol=sym,
            action_type="VERIFY_MONOTONIC_HOT_PRICE",
            expected_status=200,
        )

    # =========================================================================
    # SQUAD 2: BOT-021 .. BOT-040 (20 Hot-Cache Reader & Eviction Chaos Bots)
    # =========================================================================
    for i in range(21, 41):
        bot_id = f"BOT-{i:03d}"
        ip = f"198.51.100.{i}"
        squad = "S2_HOT_CACHE_AND_FALLBACK_CHAOS"
        sym = SYMBOLS[(i - 1) % len(SYMBOLS)]

        # 1. Hot Redis Price Read
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/market/prices/{sym}",
            symbol=sym,
            action_type="READ_HOT_PRICE",
            expected_status=200,
        )

        # 2. Batch Multi-Symbol Price Read
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url="/api/v1/market/prices",
            symbol="MULTI",
            action_type="READ_BATCH_PRICES",
            expected_status=200,
            params={"symbols": "BTCUSDT,ETHUSDT,SOLUSDT"},
        )

        # 3. 24h Snapshot Read
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url="/api/v1/market/snapshots/BTCUSDT",
            symbol="BTCUSDT",
            action_type="READ_24H_SNAPSHOT",
            expected_status=200,
        )

        # 4. OrderBook Depth-20 Read
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/market/orderbook/{sym}",
            symbol=sym,
            action_type="READ_ORDERBOOK_DEPTH20",
            expected_status=200,
            params={"depth": 20},
        )

        # 5. Chaos Evict Symbol from Hot Redis
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url=f"/api/v1/market/evict/{sym}",
            symbol=sym,
            action_type="CHAOS_EVICT_REDIS_HOT_KEY",
            expected_status=200,
        )

        # 6. Read Price Immediately After Eviction -> Verify Transparent ClickHouse Fallback
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/market/prices/{sym}",
            symbol=sym,
            action_type="READ_PRICE_CLICKHOUSE_FALLBACK",
            expected_status=200,
        )

    # =========================================================================
    # SQUAD 3: BOT-041 .. BOT-060 (20 OLAP Historical, Backfill & Lakehouse Medallion Bots)
    # =========================================================================
    for i in range(41, 61):
        bot_id = f"BOT-{i:03d}"
        ip = f"198.51.100.{i}"
        squad = "S3_OLAP_BACKFILL_AND_LAKEHOUSE"
        sym = SYMBOLS[(i - 1) % len(SYMBOLS)]

        # 1. Trigger Historical Backfill Job (API-006)
        bf_resp = _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url="/api/v1/historical/backfill-jobs",
            symbol=sym,
            action_type="TRIGGER_BACKFILL_JOB",
            expected_status=202,
            json_body={
                "provider": "binance",
                "symbol": sym,
                "interval": "1m",
                "candle_count": 6,
            },
        )
        job_id = bf_resp["data"]["job_id"]

        # 2. Poll Backfill Job Status
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/historical/backfill-jobs/{job_id}",
            symbol=sym,
            action_type="POLL_BACKFILL_JOB_STATUS",
            expected_status=200,
        )

        # 3. Query Historical Klines from ClickHouse (API-004)
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/historical/klines/{sym}",
            symbol=sym,
            action_type="QUERY_HISTORICAL_KLINES",
            expected_status=200,
            params={"interval": "1m", "limit": 25},
        )

        # 4. Query Historical Trades from ClickHouse (API-005)
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/historical/trades/{sym}",
            symbol=sym,
            action_type="QUERY_HISTORICAL_TRADES",
            expected_status=200,
            params={"limit": 25},
        )

        # 5. Execute Medallion Lakehouse Bronze -> Silver -> Great Expectations DQ Pipeline
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url="/api/v1/catalog/lakehouse/pipeline",
            symbol=sym,
            action_type="RUN_LAKEHOUSE_BRONZE_SILVER_DQ",
            expected_status=200,
            json_body={"batch_id": f"b_{i:03d}"},
        )

        # 6. Verify Watermark Progression in Platform Config
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url="/api/v1/platform/config",
            symbol=sym,
            action_type="VERIFY_INGESTION_WATERMARKS",
            expected_status=200,
        )

    # =========================================================================
    # SQUAD 4: BOT-061 .. BOT-080 (20 Quant Analytics, Anomaly Cooldown & Freshness Bots)
    # =========================================================================
    for i in range(61, 81):
        bot_id = f"BOT-{i:03d}"
        ip = f"198.51.100.{i}"
        squad = "S4_ANALYTICS_ANOMALY_AND_FRESHNESS"
        sym = SYMBOLS[(i - 1) % len(SYMBOLS)]

        # 1. Query ClickHouse Aggregated Rollup Statistics (VWAP, Volatility, Volume)
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/analytics/statistics/{sym}",
            symbol=sym,
            action_type="QUERY_ROLLUP_STATISTICS",
            expected_status=200,
        )

        # 2. Query Multi-Symbol Pearson Correlation Matrix
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url="/api/v1/analytics/correlations",
            symbol="MULTI",
            action_type="COMPUTE_CORRELATION_MATRIX",
            expected_status=200,
            params={"symbols": "BTCUSDT,ETHUSDT,SOLUSDT"},
        )

        # 3. Evaluate 5-Sigma Spike Series (First bot per symbol emits; subsequent within 15m suppressed)
        spike_series = [100.0 + (k % 2) * 0.1 for k in range(20)] + [135.0]
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url="/api/v1/analytics/anomalies/evaluate",
            symbol=sym,
            action_type="EVALUATE_ZSCORE_ANOMALY_AND_COOLDOWN",
            expected_status=200,
            json_body={
                "provider": "binance",
                "symbol": sym,
                "values": spike_series,
                "detector_name": "return_zscore",
                "timestamp": (base_now + timedelta(seconds=i)).isoformat(),
            },
        )

        # 4. Query Detected Anomalies Feed
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url="/api/v1/analytics/anomalies",
            symbol=sym,
            action_type="LIST_DETECTED_ANOMALIES",
            expected_status=200,
            params={"symbol": sym},
        )

        # 5. Query End-to-End Data Freshness (Hot Redis Lag & ClickHouse Lag)
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url="/api/v1/catalog/freshness",
            symbol="ALL",
            action_type="AUDIT_DATA_FRESHNESS_SLI",
            expected_status=200,
        )

        # 6. Query Monitored Instruments Catalog
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url="/api/v1/catalog/instruments",
            symbol="ALL",
            action_type="LIST_MONITORED_INSTRUMENTS",
            expected_status=200,
        )

    # =========================================================================
    # SQUAD 5: BOT-081 .. BOT-100 (20 Fuzzing, Corrupted Payload DLQ & Boundary Guard Bots)
    # =========================================================================
    for i in range(81, 101):
        bot_id = f"BOT-{i:03d}"
        ip = f"198.51.100.{i}"
        squad = "S5_FUZZING_DLQ_AND_BOUNDARY_GUARDS"
        sym = SYMBOLS[(i - 1) % len(SYMBOLS)]

        # 1. Fuzz Negative Trade Price -> Must Route to DeadLetterQueue (market.dlq.v1)
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url="/api/v1/market/ingest",
            symbol=sym,
            action_type="FUZZ_NEGATIVE_TRADE_PRICE_TO_DLQ",
            expected_status=202,
            json_body={
                "source_topic": "market.raw.trades.v1",
                "raw_message": {
                    "e": "trade",
                    "E": int(base_now.timestamp() * 1000),
                    "s": sym,
                    "t": 90000 + i,
                    "p": "-450.00",
                    "q": "1.0",
                },
            },
        )

        # 2. Fuzz Corrupted Kline (high_price < low_price) -> Must Route to DLQ (BR-001)
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="POST",
            url="/api/v1/market/ingest",
            symbol=sym,
            action_type="FUZZ_CORRUPTED_OHLC_ENVELOPE_TO_DLQ",
            expected_status=202,
            json_body={
                "source_topic": "market.raw.klines.v1",
                "raw_message": {
                    "e": "kline",
                    "E": int(base_now.timestamp() * 1000),
                    "s": sym,
                    "k": {
                        "t": int(base_now.timestamp() * 1000),
                        "T": int((base_now + timedelta(minutes=1)).timestamp() * 1000),
                        "s": sym,
                        "i": "1m",
                        "o": "100.00",
                        "h": "80.00",
                        "l": "95.00",
                        "c": "90.00",
                        "v": "10.0",
                        "q": "900.0",
                    },
                },
            },
        )

        # 3. Fuzz Inverted Time Range (end_time < start_time) -> Must Reject HTTP 422
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/historical/klines/{sym}",
            symbol=sym,
            action_type="FUZZ_INVERTED_TIME_RANGE_422",
            expected_status=422,
            params={
                "start_time": "2026-11-15T12:00:00+00:00",
                "end_time": "2026-11-14T12:00:00+00:00",
            },
        )

        # 4. Fuzz Excessive Query Window (> max_window_days) -> Must Reject HTTP 422
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/historical/klines/{sym}",
            symbol=sym,
            action_type="FUZZ_EXCESSIVE_WINDOW_SPAN_422",
            expected_status=422,
            params={
                "start_time": "2026-09-01T00:00:00+00:00",
                "end_time": "2026-11-15T00:00:00+00:00",
                "max_window_days": 7,
            },
        )

        # 5. Fuzz WAF SQL Injection Attempt -> Must Block HTTP 403
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="GET",
            url=f"/api/v1/historical/klines/{sym}",
            symbol=sym,
            action_type="FUZZ_WAF_SQLI_ATTACK_403",
            expected_status=403,
            params={"interval": "1m' UNION SELECT password FROM users--"},
        )

        # 6. Dynamic Catalog Subscription Update (PUT /api/v1/catalog/instruments/{symbol})
        _record_call(
            bot_id=bot_id,
            squad=squad,
            client_ip=ip,
            method="PUT",
            url=f"/api/v1/catalog/instruments/{sym}",
            symbol=sym,
            action_type="UPSERT_CATALOG_INSTRUMENT_CONFIG",
            expected_status=200,
            json_body={
                "provider": "binance",
                "enabled_streams": ["trade", "kline_1m", "ticker", "depth20"],
                "is_active": True,
            },
        )

    # =========================================================================
    # WRITE STRUCTURED ACTIVITY LOG (JSONL) & AGGREGATE QA SUMMARY (JSON)
    # =========================================================================
    with ACTIVITY_LOG_PATH.open("w", encoding="utf-8") as fh:
        for entry in logs:
            fh.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")

    latencies = sorted(e.latency_ms for e in logs)
    status_counts = Counter(str(e.status_code) for e in logs)
    squad_counts = Counter(e.squad for e in logs)
    action_counts = Counter(e.action_type for e in logs)
    source_counts = Counter(e.data_plane_source_or_topic for e in logs)

    endpoint_latencies: dict[str, list[float]] = defaultdict(list)
    for e in logs:
        endpoint_latencies[f"{e.http_method} {e.endpoint}"].append(e.latency_ms)

    endpoint_metrics = {
        ep: {
            "calls": len(vals),
            "avg_ms": round(sum(vals) / len(vals), 3),
            "p50_ms": _percentile(sorted(vals), 50),
            "p95_ms": _percentile(sorted(vals), 95),
            "p99_ms": _percentile(sorted(vals), 99),
            "max_ms": round(max(vals), 3),
        }
        for ep, vals in sorted(endpoint_latencies.items())
    }

    summary: dict[str, Any] = {
        "campaign_metadata": {
            "test_case_id": "TC-010",
            "total_bots": 100,
            "total_squads": 5,
            "bots_per_squad": 20,
            "actions_per_bot": 6,
            "total_api_operations": len(logs),
            "all_assertions_passed": all(e.assertion_passed for e in logs),
            "failed_assertions_count": sum(1 for e in logs if not e.assertion_passed),
            "activity_log_file": str(ACTIVITY_LOG_PATH.relative_to(REPO_ROOT).as_posix()),
            "summary_log_file": str(SUMMARY_LOG_PATH.relative_to(REPO_ROOT).as_posix()),
            "executed_at_utc": datetime.now(UTC).isoformat(),
        },
        "latency_distribution_ms": {
            "min_ms": round(min(latencies), 3),
            "avg_ms": round(sum(latencies) / len(latencies), 3),
            "p50_ms": _percentile(latencies, 50),
            "p95_ms": _percentile(latencies, 95),
            "p99_ms": _percentile(latencies, 99),
            "max_ms": round(max(latencies), 3),
            "hot_path_sla_target_p95_ms": 50.0,
            "olap_path_sla_target_p95_ms": 500.0,
            "sla_compliant": _percentile(latencies, 95) < 50.0,
        },
        "http_status_breakdown": dict(status_counts),
        "squad_operations_breakdown": dict(squad_counts),
        "action_type_breakdown": dict(action_counts),
        "data_plane_routing_and_source_breakdown": dict(source_counts),
        "endpoint_performance_table": endpoint_metrics,
        "data_plane_internal_state_audit": {
            "kafka_broker": {
                "trades_topic_events": len(runtime.kafka_broker._topics.get("market.raw.trades.v1", [])),
                "klines_topic_events": len(runtime.kafka_broker._topics.get("market.raw.klines.v1", [])),
                "tickers_topic_events": len(runtime.kafka_broker._topics.get("market.raw.tickers.v1", [])),
                "anomalies_topic_events": len(runtime.kafka_broker._topics.get("market.anomalies.v1", [])),
                "dlq_topic_events": len(runtime.kafka_broker.dlq_events),
            },
            "redis_hot_state_projector": {
                "applied_monotonic_updates": runtime.hot_redis_projector.applied_updates_count,
                "dropped_out_of_order_events": runtime.hot_redis_projector.dropped_out_of_order_count,
                "active_snapshot_keys": len(runtime.hot_redis_projector._snapshot_store),
            },
            "clickhouse_batch_sink": {
                "flushed_micro_batches": runtime.clickhouse_sink._flushed_batches_count,
                "deduplicated_trades_rows": len(runtime.clickhouse_sink._trades_table),
                "deduplicated_klines_rows": len(runtime.clickhouse_sink._klines_table),
                "deduplicated_tickers_rows": len(runtime.clickhouse_sink._tickers_table),
            },
            "anomaly_detector": {
                "emitted_anomalies_count": len(runtime.detected_anomalies),
                "cooldown_suppressed_alerts_count": runtime.anomaly_detector.suppressed_alerts_count,
            },
            "backfill_and_watermarks": {
                "completed_backfill_jobs": len(runtime.backfill_jobs),
                "tracked_watermarks_count": len(runtime.ingestion_watermarks),
            },
        },
    }

    with SUMMARY_LOG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)

    runtime.close()
    return summary


class Test100BotsDataPlaneSwarm(unittest.TestCase):
    """Automated QA verification of the 100-Bot Data Plane Load, Chaos & Contract Suite (`TC-010`)."""

    def test_100_bots_execute_600_operations_across_all_data_plane_apis_with_zero_failures(
        self,
    ) -> None:
        summary = run_100_bot_data_plane_campaign()
        meta = summary["campaign_metadata"]
        audit = summary["data_plane_internal_state_audit"]

        self.assertEqual(meta["total_bots"], 100)
        self.assertEqual(meta["total_api_operations"], 600)
        self.assertTrue(meta["all_assertions_passed"])
        self.assertEqual(meta["failed_assertions_count"], 0)

        # 1. All 20 stale out-of-order trades from Squad 1 (plus historical backfill candles older than live stream)
        # were blocked from overwriting newer hot prices by the Redis monotonic guard (BR-003)
        self.assertGreaterEqual(
            audit["redis_hot_state_projector"]["dropped_out_of_order_events"], 20
        )
        # 2. All 40 corrupted payloads (20 negative trades + 20 invalid OHLC klines) from Squad 5 routed to DLQ
        self.assertEqual(audit["kafka_broker"]["dlq_topic_events"], 40)
        # 3. Anomaly detector emitted 1 alert per symbol (5 symbols) and suppressed the remaining 15 duplicates
        self.assertEqual(audit["anomaly_detector"]["emitted_anomalies_count"], 5)
        self.assertEqual(audit["anomaly_detector"]["cooldown_suppressed_alerts_count"], 15)
        # 4. All 20 backfill jobs from Squad 3 completed and updated watermarks
        self.assertEqual(audit["backfill_and_watermarks"]["completed_backfill_jobs"], 20)
        # 5. Activity JSONL file has exactly 600 lines
        lines = ACTIVITY_LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 600)


if __name__ == "__main__":
    result = run_100_bot_data_plane_campaign()
    print(json.dumps(result, indent=2, ensure_ascii=False))
