"""Comprehensive Independent & Inter-Plane Integration Tests for Plane A, Plane B, and Plane C."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient
from src.agent.orchestrator.graph import (
    AgentWorkflowState,
    ReportProvenanceError,
    ReportValidator,
)
from src.agent.tools.contracts import ApprovedAgentTool
from src.agent.tools.gateway import (
    ToolQueryLimitExceededError,
    UnauthorizedToolAccessError,
    compute_deterministic_log_returns,
    compute_deterministic_pearson_correlation,
    compute_deterministic_realized_volatility,
)
from src.backend.main import create_app
from src.backend.runtime import PlatformRuntimeContainer
from src.collectors.normalizer import BinancePayloadNormalizer
from src.collectors.publisher import PartitionedEventStreamingBroker
from src.consumers.analytics_ch.main import ClickHouseBatchSink
from src.consumers.anomaly_detector import StatisticalAnomalyDetector
from src.consumers.hot_redis.main import HotStateProjector
from src.consumers.lakehouse_bronze.main import BronzeParquetArchiver
from src.processing.spark.bronze_to_silver import SilverLakehouseMergeEngine
from src.quality.expectations.suite_definitions import DataQualityGateEngine


class TestPlaneADataPlaneIndependently(unittest.IsolatedAsyncioTestCase):
    """Independent verification of Plane A (Ingestion, Kafka, Redis, ClickHouse, Lakehouse, DQ)."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="fmdp_plane_a_"))
        self.normalizer = BinancePayloadNormalizer()
        self.broker = PartitionedEventStreamingBroker(num_partitions=6)
        self.hot_projector = HotStateProjector()
        self.ch_sink = ClickHouseBatchSink(max_batch_rows=5, flush_interval_ms=1000)
        self.bronze_archiver = BronzeParquetArchiver(lakehouse_root=self.temp_dir)
        self.silver_engine = SilverLakehouseMergeEngine(lakehouse_root=self.temp_dir)
        self.dq_engine = DataQualityGateEngine()
        self.anomaly_detector = StatisticalAnomalyDetector(zscore_threshold=2.2, cooldown_seconds=900)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_normalizer_dlq_routing_and_partitioned_kafka_broker(self) -> None:
        now = datetime.now(UTC)
        valid_trade = {
            "e": "trade",
            "E": int(now.timestamp() * 1000),
            "s": "BTCUSDT",
            "t": 7001,
            "p": "91250.50000000",
            "q": "0.50000000",
            "m": False,
        }
        env, dlq = self.normalizer.normalize_or_route_dlq(
            valid_trade, source_topic="market.raw.trades.v1", ingested_at=now
        )
        self.assertIsNotNone(env)
        self.assertIsNone(dlq)
        assert env is not None
        self.assertEqual(env.payload["price"], "91250.50000000")

        p1 = await self.broker.publish_event("market.raw.trades.v1", env)
        p2 = await self.broker.publish_event("market.raw.trades.v1", env)
        self.assertEqual(p1, p2)  # Deterministic partition key {provider}:{symbol}

        polled = self.broker.poll_topic("cg.hot.redis.v1", "market.raw.trades.v1")
        self.assertEqual(len(polled), 2)
        self.broker.commit_offsets("cg.hot.redis.v1", "market.raw.trades.v1", len(polled))
        self.assertEqual(self.broker.get_topic_lag("cg.hot.redis.v1", "market.raw.trades.v1"), 0)

        # Malformed payload (negative price) -> routed to market.dlq.v1
        bad_trade = {**valid_trade, "p": "-10.00"}
        env_bad, dlq_bad = self.normalizer.normalize_or_route_dlq(
            bad_trade, source_topic="market.raw.trades.v1", ingested_at=now
        )
        self.assertIsNone(env_bad)
        self.assertIsNotNone(dlq_bad)
        assert dlq_bad is not None
        await self.broker.publish_dlq(dlq_bad)
        self.assertEqual(len(self.broker.dlq_events), 1)

    def test_hot_redis_projector_enforces_monotonic_timestamps(self) -> None:
        t_newer = datetime(2026, 11, 15, 10, 5, 0, tzinfo=UTC)
        t_older = datetime(2026, 11, 15, 10, 1, 0, tzinfo=UTC)

        env_newer = self.normalizer.normalize_ws_message(
            {
                "e": "trade",
                "s": "BTCUSDT",
                "t": 102,
                "p": "90500.00",
                "q": "1.0",
                "E": int(t_newer.timestamp() * 1000),
            },
            ingested_at=t_newer,
        )
        env_older = self.normalizer.normalize_ws_message(
            {
                "e": "trade",
                "s": "BTCUSDT",
                "t": 101,
                "p": "88000.00",
                "q": "1.0",
                "E": int(t_older.timestamp() * 1000),
            },
            ingested_at=t_older,
        )

        self.assertTrue(self.hot_projector.project_event(env_newer))
        # Out-of-order older event MUST be rejected (BR-003)
        self.assertFalse(self.hot_projector.project_event(env_older))
        self.assertEqual(self.hot_projector.dropped_out_of_order_count, 1)

        hot_price = self.hot_projector.get_hot_price("binance", "BTCUSDT")
        self.assertIsNotNone(hot_price)
        assert hot_price is not None
        self.assertEqual(hot_price.last_price, Decimal("90500.00"))

    def test_clickhouse_replacing_merge_tree_deduplication_and_bronze_to_silver_dq(self) -> None:
        open_t = datetime(2026, 11, 15, 12, 0, 0, tzinfo=UTC)
        close_t = open_t + timedelta(minutes=1)
        raw_kline_v1 = {
            "e": "kline",
            "E": int(close_t.timestamp() * 1000),
            "s": "ETHUSDT",
            "k": {
                "t": int(open_t.timestamp() * 1000),
                "T": int(close_t.timestamp() * 1000),
                "s": "ETHUSDT",
                "i": "1m",
                "o": "3100.00",
                "h": "3150.00",
                "l": "3090.00",
                "c": "3120.00",
                "v": "10.0",
                "q": "31200.0",
                "n": 40,
                "x": False,
            },
        }
        raw_kline_v2_final = {
            **raw_kline_v1,
            "E": int((close_t + timedelta(seconds=2)).timestamp() * 1000),
            "k": {**raw_kline_v1["k"], "c": "3145.50", "x": True},
        }
        env_v1 = self.normalizer.normalize_ws_message(raw_kline_v1, ingested_at=close_t)
        env_v2 = self.normalizer.normalize_ws_message(raw_kline_v2_final, ingested_at=close_t + timedelta(seconds=2))

        # Ingest both versions into ClickHouse & Bronze
        self.ch_sink.ingest_event(env_v1, auto_flush=False)
        self.ch_sink.ingest_event(env_v2, auto_flush=False)
        self.ch_sink.flush()

        rows = self.ch_sink.query_klines(
            "binance",
            "ETHUSDT",
            "1m",
            open_t - timedelta(minutes=1),
            close_t + timedelta(minutes=1),
        )
        # ReplacingMergeTree keeps only the latest version for (provider, symbol, interval, open_time)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["close_price"], Decimal("3145.50"))
        self.assertTrue(rows[0]["is_closed"])

        # Archive both in Bronze Parquet (ZSTD)
        parquet_files = self.bronze_archiver.archive_batch([env_v1, env_v2], batch_id="test_01")
        self.assertEqual(len(parquet_files), 1)
        self.assertTrue(parquet_files[0].exists())

        # Merge Bronze -> Silver and run Great Expectations quality gate
        silver_path, silver_rows = self.silver_engine.merge_bronze_klines_to_silver(parquet_files)
        self.assertTrue(silver_path.exists())
        self.assertEqual(len(silver_rows), 1)

        dq_result = self.dq_engine.validate_kline_dataset(silver_rows)
        self.assertTrue(dq_result.passed)
        self.assertTrue(dq_result.can_promote_to_gold)
        self.assertEqual(len(dq_result.failed_rule_ids), 0)

    def test_statistical_anomaly_detector_with_15m_cooldown(self) -> None:
        now = datetime(2026, 11, 15, 14, 0, 0, tzinfo=UTC)
        # 20 stable points followed by an extreme 5-sigma spike
        series = [100.0 + (i % 2) * 0.1 for i in range(20)] + [125.0]
        env_first, anom_first = self.anomaly_detector.evaluate_series("binance", "SOLUSDT", series, now_utc=now)
        self.assertIsNotNone(env_first)
        self.assertIsNotNone(anom_first)

        # Within 15-minute cooldown (e.g. +5 minutes), duplicate alert is suppressed
        env_second, _ = self.anomaly_detector.evaluate_series(
            "binance", "SOLUSDT", series, now_utc=now + timedelta(minutes=5)
        )
        self.assertIsNone(env_second)
        self.assertEqual(self.anomaly_detector.suppressed_alerts_count, 1)

        # After 16 minutes (> 900s cooldown), alert can fire again
        env_third, _ = self.anomaly_detector.evaluate_series(
            "binance", "SOLUSDT", series, now_utc=now + timedelta(minutes=16)
        )
        self.assertIsNotNone(env_third)


class TestPlaneBApplicationPlaneIndependently(unittest.TestCase):
    """Independent verification of Plane B (All 8 FastAPI Modular Monolith Domain Modules)."""

    def setUp(self) -> None:
        self.runtime = PlatformRuntimeContainer()
        self.app = create_app(runtime=self.runtime)
        self.client = TestClient(self.app)

    def test_all_eight_domain_routers_respond_according_to_api_contracts(self) -> None:
        # 1. Market module (API-001, API-002)
        r_price = self.client.get("/api/v1/market/prices/BTCUSDT")
        self.assertEqual(r_price.status_code, 200)
        self.assertEqual(r_price.json()["data"]["symbol"], "BTCUSDT")
        self.assertEqual(r_price.json()["meta"]["source"], "redis_hot_cache")

        r_snap = self.client.get("/api/v1/market/snapshots/BTCUSDT")
        self.assertEqual(r_snap.status_code, 200)
        self.assertIn("high_24h", r_snap.json()["data"])

        r_ob = self.client.get("/api/v1/market/orderbook/BTCUSDT?depth=10")
        self.assertEqual(r_ob.status_code, 200)
        self.assertEqual(r_ob.json()["meta"]["depth"], 10)

        # 2. Historical module (API-004, BoundedTimeRange guard)
        r_klines = self.client.get("/api/v1/historical/klines/BTCUSDT?interval=1m&limit=10")
        self.assertEqual(r_klines.status_code, 200)
        self.assertGreaterEqual(r_klines.json()["meta"]["count"], 1)

        # Invalid time range (end_time < start_time) must return 422
        r_invalid_range = self.client.get(
            "/api/v1/historical/klines/BTCUSDT",
            params={
                "start_time": "2026-11-15T12:00:00+00:00",
                "end_time": "2026-11-14T12:00:00+00:00",
            },
        )
        self.assertEqual(r_invalid_range.status_code, 422)

        # 3. Analytics module (API-007)
        r_stats = self.client.get("/api/v1/analytics/statistics/BTCUSDT")
        self.assertEqual(r_stats.status_code, 200)
        self.assertIn("vwap", r_stats.json()["data"])

        r_corr = self.client.get("/api/v1/analytics/correlations?symbols=BTCUSDT,ETHUSDT")
        self.assertEqual(r_corr.status_code, 200)
        self.assertEqual(r_corr.json()["data"]["matrix"]["BTCUSDT"]["BTCUSDT"], 1.0)

        # 4. Catalog module
        r_inst = self.client.get("/api/v1/catalog/instruments")
        self.assertEqual(r_inst.status_code, 200)
        self.assertGreaterEqual(r_inst.json()["meta"]["count"], 5)

        r_fresh = self.client.get("/api/v1/catalog/freshness")
        self.assertEqual(r_fresh.status_code, 200)
        self.assertTrue(r_fresh.json()["data"][0]["is_healthy"])

        # 5. Platform Config module
        r_cfg = self.client.get("/api/v1/platform/config")
        self.assertEqual(r_cfg.status_code, 200)
        self.assertIn("BTCUSDT", r_cfg.json()["data"]["active_symbols"])


class TestPlaneCIntelligencePlaneIndependently(unittest.IsolatedAsyncioTestCase):
    """Independent verification of Plane C (ControlledToolGateway, LangGraph 5-Node State Machine, Citations)."""

    def setUp(self) -> None:
        self.runtime = PlatformRuntimeContainer()

    async def test_controlled_tool_gateway_determinism_and_guardrails(self) -> None:
        # Deterministic math functions
        rets = compute_deterministic_log_returns([100.0, 105.0, 110.25])
        self.assertEqual(len(rets), 2)
        vol = compute_deterministic_realized_volatility([100.0, 102.0, 101.0, 103.0])
        self.assertGreater(vol, 0.0)
        corr = compute_deterministic_pearson_correlation([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
        self.assertAlmostEqual(corr, 1.0, places=5)

        perms = frozenset({"market:read", "historical:read", "analytics:read", "agent:trigger"})

        # Unapproved tool name is strictly rejected
        with self.assertRaises(UnauthorizedToolAccessError):
            await self.runtime.tool_gateway.execute_tool(
                "execute_sql_raw", {"query": "SELECT 1"}, granted_permissions=perms
            )

        # Excessive row limit is strictly rejected
        with self.assertRaises(ToolQueryLimitExceededError):
            await self.runtime.tool_gateway.execute_tool(
                ApprovedAgentTool.GET_HISTORICAL_CANDLES.value,
                {"symbol": "BTCUSDT", "limit": 999999},
                granted_permissions=perms,
            )

    async def test_langgraph_five_node_workflow_and_citation_verification(self) -> None:
        # 1. Valid symbol investigation completes all 5 nodes
        state = AgentWorkflowState(
            run_id="run_test_001",
            trigger_mode="ON_DEMAND",
            symbol="BTCUSDT",
            prompt_summary="Analyze BTCUSDT volatility and anomalies",
        )
        completed = await self.runtime.intelligence_graph.run_investigation(state)
        self.assertEqual(completed.status, "COMPLETED")
        self.assertIn("intake_and_guardrail_node", completed.visited_nodes)
        self.assertIn("report_synthesizer_node", completed.visited_nodes)
        self.assertEqual(len(completed.evidence_trail), 8)  # 7 investigation tools + 1 persist tool
        self.assertIsNotNone(completed.final_report)
        assert completed.final_report is not None
        self.assertEqual(len(completed.final_report["provenance_citations"]), 7)

        # 2. Guardrail node rejects unmonitored symbol
        rejected_state = AgentWorkflowState(
            run_id="run_test_002",
            trigger_mode="ON_DEMAND",
            symbol="DOGEFAKEUSDT",
            prompt_summary="Analyze unmonitored symbol",
        )
        rejected = await self.runtime.intelligence_graph.run_investigation(rejected_state)
        self.assertEqual(rejected.status, "FAILED")

        # 3. ReportValidator rejects fabricated citation IDs
        bad_report = {
            **completed.final_report,
            "provenance_citations": [
                {
                    "invocation_id": "inv_fabricated_999999",
                    "tool_name": "get_latest_price",
                    "source_store": "redis",
                    "symbol": "BTCUSDT",
                    "window_start": datetime.now(UTC).isoformat(),
                    "window_end": datetime.now(UTC).isoformat(),
                    "row_count": 1,
                }
            ],
        }
        with self.assertRaises(ReportProvenanceError):
            ReportValidator.validate_report(bad_report, completed.evidence_trail)


class TestInterPlaneCommunicationEndToEnd(unittest.TestCase):
    """End-to-end verification of communication across Plane A <-> Plane B <-> Plane C."""

    def setUp(self) -> None:
        self.runtime = PlatformRuntimeContainer()
        self.app = create_app(runtime=self.runtime)
        self.client = TestClient(self.app)

    def test_plane_a_to_plane_b_hot_cache_and_transparent_clickhouse_fallback(self) -> None:
        # Step 1: Query hot price from Redis (seeded via Plane A)
        res_hot = self.client.get("/api/v1/market/prices/BTCUSDT")
        self.assertEqual(res_hot.status_code, 200)
        self.assertEqual(res_hot.json()["meta"]["source"], "redis_hot_cache")

        # Step 2: Simulate Redis hot key eviction / cache miss
        self.runtime.hot_redis_projector.evict_hot_symbol("binance", "BTCUSDT")

        # Step 3: Query Plane B again -> automatically falls back to ClickHouse OLAP (ADR-005)
        res_fallback = self.client.get("/api/v1/market/prices/BTCUSDT")
        self.assertEqual(res_fallback.status_code, 200)
        self.assertEqual(res_fallback.json()["meta"]["source"], "clickhouse_fallback")
        self.assertEqual(res_fallback.json()["data"]["symbol"], "BTCUSDT")

    def test_plane_b_backfill_triggers_plane_a_and_plane_c_investigation_generates_report(
        self,
    ) -> None:
        # Step 1: Trigger Historical Backfill Job via Plane B (API-006)
        bf_res = self.client.post(
            "/api/v1/historical/backfill-jobs",
            json={"provider": "binance", "symbol": "SOLUSDT", "interval": "1m", "candle_count": 8},
        )
        self.assertEqual(bf_res.status_code, 202)
        job_id = bf_res.json()["data"]["job_id"]
        self.assertEqual(bf_res.json()["data"]["ingested_candles"], 8)

        # Verify job status and watermark update in Plane B
        job_status = self.client.get(f"/api/v1/historical/backfill-jobs/{job_id}")
        self.assertEqual(job_status.status_code, 200)
        self.assertEqual(job_status.json()["data"]["status"], "COMPLETED")

        # Step 2: Trigger Asynchronous Plane C Agent Investigation via Plane B (API-008) with Idempotency-Key
        headers = {"Idempotency-Key": "idem-sol-investigation-001"}
        run_res_1 = self.client.post(
            "/api/v1/agents/runs",
            json={
                "symbol": "SOLUSDT",
                "prompt_summary": "Investigate SOLUSDT post-backfill price dynamics",
                "trigger_mode": "ON_DEMAND",
            },
            headers=headers,
        )
        self.assertEqual(run_res_1.status_code, 202)
        run_id = run_res_1.json()["data"]["run_id"]
        self.assertEqual(run_res_1.json()["data"]["status"], "COMPLETED")

        # Duplicate request with same Idempotency-Key returns the exact same run_id
        run_res_2 = self.client.post(
            "/api/v1/agents/runs",
            json={"symbol": "SOLUSDT", "prompt_summary": "Duplicate request"},
            headers=headers,
        )
        self.assertEqual(run_res_2.status_code, 202)
        self.assertEqual(run_res_2.json()["data"]["run_id"], run_id)

        # Step 3: Stream SSE events for the completed run
        sse_res = self.client.get(f"/api/v1/agents/runs/{run_id}/events")
        self.assertEqual(sse_res.status_code, 200)
        self.assertIn("event: tool_invocation", sse_res.text)
        self.assertIn("event: run_completed", sse_res.text)

        # Step 4: Retrieve the persisted StructuredAnalysisReport from Plane B Reporting module
        rep_res = self.client.get(f"/api/v1/reports/{run_id}")
        self.assertEqual(rep_res.status_code, 200)
        rep_data = rep_res.json()["data"]
        self.assertEqual(rep_data["symbol"], "SOLUSDT")
        self.assertEqual(len(rep_data["provenance_citations"]), 7)
        self.assertIn("Deterministic market intelligence report", rep_data["summary"])


if __name__ == "__main__":
    unittest.main()
