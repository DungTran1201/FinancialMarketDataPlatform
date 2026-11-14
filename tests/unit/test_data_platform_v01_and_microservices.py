"""TC-011: Verification of Zero-Mock Data Platform v0.1 (Stages 1..12) & Domain Microservices (ADR-007)."""

from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
from src.backend.main import create_app
from src.backend.runtime import PlatformRuntimeContainer
from src.collectors.main_rest import HistoricalRestBackfillWorker, IngestionWatermarkStore
from src.collectors.main_ws import WebSocketStreamCollector, compute_reconnect_backoff_seconds
from src.collectors.publisher import (
    PartitionedEventStreamingBroker,
    ProductionExchangeHistoricalCollector,
)
from src.processing.pipeline_v01 import DataPlatformV01Pipeline


class TestDataPlatformV01AndMicroservices(unittest.TestCase):
    """End-to-End verification for Data Platform v0.1 (12 Stages, Zero Mocks) and Domain Microservices."""

    def test_stage1_discovery_gap_detection_and_watermarks(self) -> None:
        """Verify Stage 1 exchangeInfo discovery, Stage 2 WS gap detection, and SQLite watermark persistence."""

        async def _scenario() -> None:
            broker = PartitionedEventStreamingBroker(num_partitions=6)
            collector = ProductionExchangeHistoricalCollector()

            # Stage 1: Exchange metadata discovery via real HTTP ASGI protocol
            discovered = await collector.discover_exchange_metadata()
            self.assertIn("BTCUSDT", discovered)
            self.assertIn("ETHUSDT", discovered)
            self.assertEqual(discovered["BTCUSDT"].status, "TRADING")
            self.assertGreaterEqual(collector.rate_limiter.used_weight, 10)

            # Stage 2a: WebSocket collector + sequence gap detection + reconnect backoff
            ws = WebSocketStreamCollector(broker=broker)
            backoff = compute_reconnect_backoff_seconds(attempt=2, deterministic_jitter=0.5)
            self.assertAlmostEqual(backoff, 4.5, places=3)

            t0 = datetime(2026, 11, 15, 0, 0, tzinfo=UTC)
            t1_skipped = t0 + timedelta(minutes=4)  # Skips 3 candles (00:01, 00:02, 00:03)

            frame_0 = {
                "e": "kline",
                "E": int((t0 + timedelta(minutes=1)).timestamp() * 1000),
                "s": "BTCUSDT",
                "k": {
                    "t": int(t0.timestamp() * 1000),
                    "T": int((t0 + timedelta(minutes=1)).timestamp() * 1000),
                    "s": "BTCUSDT",
                    "i": "1m",
                    "o": "89000.00",
                    "h": "89100.00",
                    "l": "88950.00",
                    "c": "89050.00",
                    "v": "10.5",
                    "q": "935025.00",
                    "n": 50,
                    "x": True,
                },
            }
            frame_1 = {
                "e": "kline",
                "E": int((t1_skipped + timedelta(minutes=1)).timestamp() * 1000),
                "s": "BTCUSDT",
                "k": {
                    "t": int(t1_skipped.timestamp() * 1000),
                    "T": int((t1_skipped + timedelta(minutes=1)).timestamp() * 1000),
                    "s": "BTCUSDT",
                    "i": "1m",
                    "o": "89050.00",
                    "h": "89200.00",
                    "l": "89000.00",
                    "c": "89150.00",
                    "v": "12.0",
                    "q": "1069800.00",
                    "n": 60,
                    "x": True,
                },
            }

            _, gap0 = await ws.process_ws_frame(frame_0, ingested_at=t0)
            self.assertIsNone(gap0)
            _, gap1 = await ws.process_ws_frame(frame_1, ingested_at=t1_skipped)
            self.assertIsNotNone(gap1)
            assert gap1 is not None
            self.assertEqual(gap1.missing_candles, 3)

            # Stage 2b: REST backfill of the detected gap + SQLite watermark checkpointing
            wm_store = IngestionWatermarkStore(":memory:")
            rest_worker = HistoricalRestBackfillWorker(
                collector=collector, broker=broker, watermark_store=wm_store
            )
            bf_res = await rest_worker.execute_backfill(
                symbol="BTCUSDT",
                interval="1m",
                start_time=gap1.gap_start,
                end_time=gap1.gap_end,
            )
            self.assertEqual(bf_res["events_published"], 3)
            wm = wm_store.get_watermark("binance", "BTCUSDT", "1m")
            self.assertIsNotNone(wm)
            assert wm is not None
            self.assertEqual(wm.status, "SYNCED")

        asyncio.run(_scenario())

    def test_end_to_end_12_stage_data_platform_v01_pipeline(self) -> None:
        """Verify 12-stage execution: Discovery -> Kafka -> Bronze -> Silver -> Gold -> Compaction -> Lineage."""

        async def _scenario() -> None:
            with tempfile.TemporaryDirectory() as tmp_dir:
                lh_root = Path(tmp_dir) / "lakehouse_v01"
                pipeline = DataPlatformV01Pipeline(lakehouse_root=lh_root)
                report = await pipeline.run_end_to_end_pipeline(
                    symbols=("BTCUSDT", "ETHUSDT"),
                    interval="1m",
                    backfill_minutes=5,
                )

                self.assertEqual(report.stage_01_discovered_symbols, 5)
                self.assertGreaterEqual(report.stage_02_ingested_ws_events, 4)
                self.assertEqual(report.stage_02_backfilled_rest_events, 10)
                self.assertGreaterEqual(report.stage_05_bronze_parquet_files, 3)
                self.assertEqual(report.stage_06_silver_klines_rows, 10)
                self.assertEqual(report.stage_06_silver_trades_rows, 2)
                self.assertTrue(report.stage_08_dq_passed)
                self.assertTrue(report.stage_10_serving_ready)

                # Verify Gold Analytical Marts (Stage 7)
                self.assertGreaterEqual(report.stage_07_gold_marts_rows["fct_daily_market_summary"], 2)
                self.assertEqual(report.stage_07_gold_marts_rows["fct_realized_volatility"], 2)
                self.assertEqual(report.stage_07_gold_marts_rows["fct_orderbook_liquidity"], 2)

                btc_summary = pipeline.gold_mart_engine.query_gold_mart(
                    "fct_daily_market_summary", symbol="BTCUSDT"
                )
                self.assertGreaterEqual(len(btc_summary), 1)
                self.assertGreater(btc_summary[0]["daily_vwap"], 0.0)

                # Verify Stage 9 Apache Iceberg v2 metadata manifests exist on disk
                meta_files = list((lh_root / "silver" / "market_klines" / "metadata").glob("*.metadata.json"))
                self.assertEqual(len(meta_files), 1)
                manifest = json.loads(meta_files[0].read_text(encoding="utf-8"))
                self.assertEqual(manifest["format-version"], 2)
                self.assertEqual(manifest["table-identifier"], "lakehouse.silver.market_klines")

                # Verify Stage 11 Prometheus Metrics & Stage 12 Lineage Catalog
                prom_text = pipeline.observability.export_prometheus_text()
                self.assertIn("fmdp_ingested_events_total", prom_text)
                self.assertIn("fmdp_gold_mart_rows_total", prom_text)

                lineage = pipeline.lineage_registry.export_lineage_catalog()
                self.assertEqual(lineage["total_datasets"], 12)
                self.assertGreaterEqual(lineage["total_lineage_edges"], 10)

        asyncio.run(_scenario())

    def test_microservices_decomposition_and_gateway_routing(self) -> None:
        """Verify standalone execution of all 8 domain microservices and unified API Gateway routing."""

        async def _scenario() -> None:
            rt = PlatformRuntimeContainer()
            gateway_app = create_app(runtime=rt)
            headers = {
                "Host": "api.fmdp.local",
                "X-Forwarded-Proto": "https",
                "X-Forwarded-For": "10.20.30.40",
            }

            transport = httpx.ASGITransport(app=gateway_app)
            async with httpx.AsyncClient(
                transport=transport, base_url="https://api.fmdp.local", headers=headers
            ) as client:
                # 1. Verify Microservices Topology Manifest (API-015)
                topo_resp = await client.get("/api/v1/microservices/topology")
                self.assertEqual(topo_resp.status_code, 200)
                topo = topo_resp.json()
                self.assertEqual(topo["architecture_style"], "domain_microservices_v01")
                self.assertEqual(topo["total_microservices"], 8)
                for svc in topo["services"]:
                    self.assertEqual(svc["status"], "ONLINE")
                    self.assertTrue(svc["encrypted_binding"]["encrypted_endpoint"].startswith("enc_v1_"))

                # 2. Verify Health Probe across all 7 domain microservices via Gateway
                health_resp = await client.get("/api/v1/microservices/health")
                self.assertEqual(health_resp.status_code, 200)
                h_data = health_resp.json()
                self.assertTrue(h_data["all_healthy"])
                self.assertEqual(len(h_data["microservices"]), 7)

                # 3. Verify Direct Inter-Service Dispatch to isolated `svc-market-hot`
                disp_resp = await client.post(
                    "/api/v1/microservices/dispatch/svc-market-hot",
                    json={"method": "GET", "path": "/api/v1/market/prices/BTCUSDT"},
                )
                self.assertEqual(disp_resp.status_code, 200)
                disp_data = disp_resp.json()
                self.assertEqual(disp_data["service_id"], "svc-market-hot")
                self.assertEqual(disp_data["status_code"], 200)
                self.assertEqual(disp_data["payload"]["data"]["symbol"], "BTCUSDT")

                # 4. Trigger End-to-End Data Platform v0.1 Run via `svc-data-plane-v01` (API-011..014)
                run_resp = await client.post(
                    "/api/v1/data-platform/v01/run",
                    json={"symbols": ["BTCUSDT", "ETHUSDT"], "interval": "1m", "backfill_minutes": 4},
                )
                self.assertEqual(run_resp.status_code, 200)
                run_data = run_resp.json()
                self.assertTrue(run_data["stages"]["stage_08_quality_gates"]["passed"])
                self.assertTrue(run_data["stages"]["stage_10_serving_readiness"]["serving_ready"])

                # Query Gold Marts (API-012)
                gold_resp = await client.get(
                    "/api/v1/data-platform/v01/gold/fct_daily_market_summary?symbol=BTCUSDT"
                )
                self.assertEqual(gold_resp.status_code, 200)
                self.assertGreaterEqual(gold_resp.json()["row_count"], 1)

                # Trigger Compaction (API-013)
                comp_resp = await client.post(
                    "/api/v1/data-platform/v01/compaction",
                    json={"layer": "silver", "table_name": "market_klines"},
                )
                self.assertEqual(comp_resp.status_code, 200)
                self.assertEqual(comp_resp.json()["compression_codec"], "ZSTD")

                # Query Governance Lineage (API-014) & Watermarks & Metrics
                lin_resp = await client.get("/api/v1/data-platform/v01/lineage")
                self.assertEqual(lin_resp.status_code, 200)
                self.assertEqual(lin_resp.json()["total_datasets"], 12)

                wm_resp = await client.get("/api/v1/data-platform/v01/watermarks")
                self.assertEqual(wm_resp.status_code, 200)
                self.assertGreaterEqual(wm_resp.json()["count"], 2)

                met_resp = await client.get("/api/v1/data-platform/v01/metrics")
                self.assertEqual(met_resp.status_code, 200)
                self.assertIn("fmdp_ingested_events_total", met_resp.text)

        asyncio.run(_scenario())


if __name__ == "__main__":
    unittest.main()
