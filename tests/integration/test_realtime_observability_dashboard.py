"""Integration tests for FEAT-001 Real-Time Data Platform Observatory & Data Flow Visualization."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient
from src.serving.api.main import create_app
from src.shared.observability.tracing import compute_parallel_branch_latencies


def test_parallel_branch_latency_never_sums_sink_branches() -> None:
    """Prove E2E Serving latency takes critical max across parallel sink branches, not their sum."""
    timings = {
        "ingestion": 0.2,
        "kafka_publish": 0.3,
        "kafka_consume": 0.1,
        "redis_hot_write": 1.0,
        "clickhouse_olap_write": 2.5,
        "bronze_archive": 3.0,
        "silver_merge": 2.0,
        "dq_gate": 0.5,
        "gold_mart": 1.5,
        "serving_ready": 0.1,
    }
    res = compute_parallel_branch_latencies(timings, final_status="SERVING_COMPLETE")
    assert res["serial_spine_ms"] == 0.6
    assert res["hot_branch_ms"] == 1.0
    assert res["olap_branch_ms"] == 2.5
    assert res["lakehouse_branch_ms"] == 7.0
    assert res["serving_hot_e2e_ms"] == 1.7
    assert res["serving_olap_e2e_ms"] == 3.2
    assert res["serving_lakehouse_e2e_ms"] == 7.7
    # Serial spine (0.6) + max parallel branch (7.0) + serving_ready (0.1) = 7.7 (NOT 11.2!)
    assert res["end_to_end_serving_ms"] == 7.7


@pytest.mark.asyncio
async def test_observatory_ui_csp_sse_and_passive_non_mutation() -> None:
    """Verify UI shell is decommissioned (404), API stays strict default-src none, and GET does not mutate."""
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost:8000") as client:
        # 1. Verify demo UI routes are completely decommissioned (404)
        ui_resp = await client.get("/ui/data-flow")
        assert ui_resp.status_code == 404

        css_resp = await client.get("/ui/assets/observatory.css")
        assert css_resp.status_code == 404
        js_resp = await client.get("/ui/assets/observatory.js")
        assert js_resp.status_code == 404

        # 2. Passive telemetry GET keeps API strict CSP and does not inject fake events
        ov1 = await client.get("/api/v1/observability/overview")
        assert ov1.status_code == 200
        assert "default-src 'none'" in ov1.headers.get("content-security-policy", "")
        ov2 = await client.get("/api/v1/observability/overview")
        assert ov2.status_code == 200
        assert ov1.json()["kpis"]["events_ingested"] == ov2.json()["kpis"]["events_ingested"]

        # 3. Finite SSE snapshot verification
        sse_resp = await client.get("/api/v1/observability/stream?max_events=1")
        assert sse_resp.status_code == 200
        assert "event: snapshot" in sse_resp.text
        assert '"topology"' in sse_resp.text

        # 4. Honest Kafka 1-node KRaft Broker 2/3 UNAVAILABLE reporting
        topo = (await client.get("/api/v1/observability/topology")).json()
        kafka_node = next(n for n in topo["nodes"] if n["id"] == "kafka_cluster")
        assert kafka_node["brokers"][1]["status"] == "UNAVAILABLE"
        assert kafka_node["brokers"][2]["status"] == "UNAVAILABLE"


@pytest.mark.asyncio
async def test_observatory_end_to_end_trace_lag_lakehouse_dlq_and_rollup() -> None:
    """Verify full trace lifecycle, Kafka Bronze lag -> commit, Iceberg manifests, DLQ, and 5m rollup."""
    app = create_app()
    rt = app.state.runtime
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost:8000") as client:
        # 1. Explicit DEMO batch emit -> Hot + ClickHouse commit immediately; Bronze lags > 0
        emit_res = await client.post(
            "/api/v1/observability/demo/emit",
            json={"action": "emit_batch", "symbol": "ETHUSDT", "count": 3},
        )
        assert emit_res.status_code == 200
        emitted_ids = emit_res.json()["event_ids"]
        assert len(emitted_ids) == 3

        kf_before = (await client.get("/api/v1/observability/kafka?topic=market.raw.trades.v1")).json()
        cgs_before = {c["consumer_group"]: c for c in kf_before["selected_topic_detail"]["consumer_groups"]}
        assert cgs_before["cg.hot.redis.v1"]["lag"] == 0
        assert cgs_before["cg.analytics.clickhouse.v1"]["lag"] == 0
        assert cgs_before["cg.lakehouse.bronze.v1"]["lag"] >= 3

        tr_hot = (await client.get(f"/api/v1/observability/traces/{emitted_ids[0]}")).json()
        assert tr_hot["final_status"] == "SERVING_HOT"
        assert tr_hot["execution_mode"] == "DEMO"
        assert tr_hot["timestamps"]["redis_written_at"] is not None
        assert tr_hot["timestamps"]["clickhouse_written_at"] is not None
        assert tr_hot["timestamps"]["bronze_committed_at"] is None
        assert tr_hot["hot_branch_ms"] is not None
        assert tr_hot["olap_branch_ms"] is not None

        # 2. Flush Bronze -> Silver -> Gold -> verify lag drops to 0 and trace upgrades to SERVING_COMPLETE
        flush_res = await client.post(
            "/api/v1/observability/demo/emit",
            json={"action": "flush_lakehouse", "symbol": "ETHUSDT"},
        )
        assert flush_res.status_code == 200

        kf_after = (await client.get("/api/v1/observability/kafka?topic=market.raw.trades.v1")).json()
        cgs_after = {c["consumer_group"]: c for c in kf_after["selected_topic_detail"]["consumer_groups"]}
        assert cgs_after["cg.lakehouse.bronze.v1"]["lag"] == 0

        tr_done = (await client.get(f"/api/v1/observability/traces/{emitted_ids[0]}")).json()
        assert tr_done["final_status"] == "SERVING_COMPLETE"
        assert tr_done["timestamps"]["bronze_committed_at"] is not None
        assert tr_done["timestamps"]["silver_processed_at"] is not None
        assert tr_done["lakehouse_branch_ms"] is not None
        assert "cg.lakehouse.bronze.v1" in tr_done["consumer_groups_acked"]

        # 3. Verify Lakehouse storage & Iceberg v2 manifests on disk
        storage = (await client.get("/api/v1/observability/storage")).json()
        assert storage["lakehouse"]["bronze"]["file_count"] >= 1
        assert len(storage["lakehouse"]["iceberg_manifests"]) >= 1
        assert any(m.get("format_version") == 2 for m in storage["lakehouse"]["iceberg_manifests"])

        # 4. Inject DLQ fault -> recorded in traces & DLQ topic
        dlq_res = await client.post(
            "/api/v1/observability/demo/emit",
            json={"action": "inject_dlq", "symbol": "ETHUSDT"},
        )
        assert dlq_res.status_code == 200
        dlq_traces = (await client.get("/api/v1/observability/traces?status=DLQ_FAILED")).json()
        assert dlq_traces["count"] >= 1

        # 5. Deterministic Decimal 5m OHLCV rollup without fake candles for uningested symbols
        now_utc = datetime.now(UTC).replace(second=0, microsecond=0)
        # Align base_t cleanly to a 5-minute epoch boundary 10 minutes ago
        base_epoch = (int(now_utc.timestamp()) // 300) * 300 - 600
        base_t = datetime.fromtimestamp(base_epoch, tz=UTC)
        bars = [
            (0, "100.00", "105.00", "99.00", "103.00", "2.00"),
            (1, "103.00", "108.00", "101.00", "106.00", "3.00"),
            (2, "106.00", "107.00", "100.00", "102.00", "1.00"),
        ]
        for mins, o, h, lo, c, v in bars:
            t_open = int((base_t + timedelta(minutes=mins)).timestamp() * 1000)
            t_close = t_open + 59_999
            await rt.ingest_raw_provider_message(
                {
                    "e": "kline",
                    "E": t_close,
                    "s": "AVAXUSDT",
                    "k": {
                        "t": t_open,
                        "T": t_close,
                        "i": "1m",
                        "o": o,
                        "h": h,
                        "l": lo,
                        "c": c,
                        "v": v,
                        "q": "100.00",
                        "n": 10,
                    },
                },
                source_topic="market.raw.klines.v1",
                execution_mode="LIVE",
            )
        rollup_resp = await client.get("/api/v1/observability/candles?symbol=AVAXUSDT&interval=5m&hours=24")
        assert rollup_resp.status_code == 200
        rolled = rollup_resp.json()["candles"]
        assert len(rolled) == 1
        assert rolled[0]["open"] == 100.0
        assert rolled[0]["high"] == 108.0
        assert rolled[0]["low"] == 99.0
        assert rolled[0]["close"] == 102.0
        assert rolled[0]["volume"] == 6.0
        assert rolled[0]["rolled_up_from_bars"] == 3

        empty_resp = await client.get("/api/v1/observability/candles?symbol=FAKECOINUSDT&interval=1m")
        assert empty_resp.status_code == 200
        assert empty_resp.json()["candles"] == []
        assert empty_resp.json()["no_fake_candles_policy"] is True

        # 6. Bounded Prometheus cardinality check (no event_id in Prometheus output)
        prom_text = (await client.get("/metrics")).text
        assert "fmdp_stage_processing_duration_ms_bucket" in prom_text
        assert "fmdp_end_to_end_latency_ms_bucket" in prom_text
        assert "event_id=" not in prom_text

        # 7. Graceful UNAVAILABLE reporting when Binance network pull fails
        with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Air-gapped")):
            probe_res = await client.post(
                "/api/v1/observability/live/probe",
                json={"symbol": "BTCUSDT", "fetch_binance": True},
            )
            assert probe_res.status_code == 200
            assert probe_res.json()["binance_live_pull"]["status"] == "UNAVAILABLE"

        # 8. Full 12-stage pipeline + Latency analytics buckets & branch stats
        pipe_res = await client.post(
            "/api/v1/observability/demo/emit",
            json={"action": "run_full_pipeline", "symbol": "BTCUSDT"},
        )
        assert pipe_res.status_code == 200
        assert pipe_res.json()["execution_mode"] == "DEMO"

        lat = (await client.get("/api/v1/observability/latency")).json()
        assert lat["trace_count"] >= 5
        assert lat["branch_stats"]["end_to_end_serving_ms"]["p50"] is not None
        assert len(lat["timeseries_buckets"]) >= 1
        assert len(lat["timeseries_buckets"][0]["event_ids"]) >= 1
        bucket_eid = lat["timeseries_buckets"][0]["event_ids"][0]
        bucket_trace = await client.get(f"/api/v1/observability/traces/{bucket_eid}")
        assert bucket_trace.status_code == 200


def test_observability_websocket_snapshot_and_ping_pong() -> None:
    """Verify WebSocket /ws/v1/observability/stream emits initial snapshot and responds pong to ping."""
    app = create_app()
    with TestClient(app) as client, client.websocket_connect("/ws/v1/observability/stream") as ws:
        snap = ws.receive_json()
        assert snap["type"] == "snapshot"
        assert "overview" in snap
        ws.send_json({"type": "ping", "timestamp": 123456})
        pong = ws.receive_json()
        assert pong == {"type": "pong", "timestamp": 123456}

