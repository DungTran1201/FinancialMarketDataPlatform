"""Resilience Tests: Stream Gap Recovery, Watermark Healing, DLQ Routing & Anomaly Cooldown (`TC-013`)."""

from __future__ import annotations

import asyncio
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from src.ingestion.application.backfill_service import HistoricalRestBackfillWorker
from src.ingestion.application.ws_service import WebSocketStreamCollector
from src.ingestion.infrastructure.watermark_store import IngestionWatermarkStore
from src.ingestion.providers.binance.rest_client import ProductionExchangeHistoricalCollector
from src.shared.contracts.events.market_events import (
    SCHEMA_VERSION_V1,
    EventEnvelopeV1,
    EventType,
    compute_deterministic_event_id,
)
from src.streaming.consumers.anomaly_detector import StatisticalAnomalyDetector
from src.streaming.consumers.hot_redis import HotStateProjector
from src.streaming.infrastructure.kafka_broker import PartitionedEventStreamingBroker


class TestStreamingAndIngestionResilience(unittest.TestCase):
    """Validates fault recovery across ingestion gaps, DLQ isolation, and monotonic projection."""

    def test_ws_gap_triggers_watermark_and_rest_backfill_healing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wm_store = IngestionWatermarkStore(db_path=Path(tmp) / "wm.db")
            try:
                broker = PartitionedEventStreamingBroker()
                collector = ProductionExchangeHistoricalCollector(
                    use_embedded_asgi_transport=True
                )
                backfill = HistoricalRestBackfillWorker(
                    collector=collector,
                    broker=broker,
                    watermark_store=wm_store,
                )
                ws = WebSocketStreamCollector(
                    broker=broker,
                    backfill_worker=backfill,
                    watermark_store=wm_store,
                )
                t0 = datetime(2026, 11, 15, 0, 0, tzinfo=UTC)
                t3 = t0 + timedelta(minutes=3)

                async def _run() -> object:
                    await ws.process_ws_frame(
                        {
                            "e": "kline",
                            "E": int(t0.timestamp() * 1000),
                            "s": "BTCUSDT",
                            "k": {
                                "i": "1m",
                                "t": int(t0.timestamp() * 1000),
                                "T": int((t0 + timedelta(minutes=1)).timestamp() * 1000),
                                "o": "89000",
                                "h": "89100",
                                "l": "88900",
                                "c": "89050",
                                "v": "5",
                                "q": "445000",
                                "n": 10,
                                "x": True,
                            },
                        }
                    )
                    _, gap = await ws.process_ws_frame(
                        {
                            "e": "kline",
                            "E": int(t3.timestamp() * 1000),
                            "s": "BTCUSDT",
                            "k": {
                                "i": "1m",
                                "t": int(t3.timestamp() * 1000),
                                "T": int((t3 + timedelta(minutes=1)).timestamp() * 1000),
                                "o": "89200",
                                "h": "89300",
                                "l": "89100",
                                "c": "89250",
                                "v": "6",
                                "q": "535000",
                                "n": 12,
                                "x": True,
                            },
                        }
                    )
                    return gap

                gap = asyncio.run(_run())
                self.assertIsNotNone(gap)
                wm = wm_store.get_watermark("binance", "BTCUSDT", "1m")
                self.assertIsNotNone(wm)
                assert wm is not None
                self.assertEqual(wm.status, "SYNCED")
            finally:
                wm_store.close()

    def test_corrupt_ws_frame_routed_to_dlq_and_monotonic_hot_state_drops_stale(self) -> None:
        broker = PartitionedEventStreamingBroker()
        ws = WebSocketStreamCollector(broker=broker)
        env, gap = asyncio.run(
            ws.process_ws_frame(
                {"s": "BTCUSDT", "E": 1700000000000, "p": "-10.0", "q": "1.0", "t": 1}
            )
        )
        self.assertIsNone(env)
        self.assertIsNone(gap)
        self.assertEqual(len(broker.dlq_events), 1)

        projector = HotStateProjector()
        t_new = datetime(2026, 11, 15, 2, 0, tzinfo=UTC)
        t_old = t_new - timedelta(seconds=30)
        new_env = EventEnvelopeV1(
            event_id=str(compute_deterministic_event_id("binance", EventType.TRADE, "BTCUSDT", "2002")),
            event_type=EventType.TRADE,
            schema_version=SCHEMA_VERSION_V1,
            provider="binance",
            symbol="BTCUSDT",
            exchange_event_time=t_new,
            ingested_at=t_new,
            sequence_id=2,
            payload={"trade_id": "2002", "price": "90000", "quantity": "1.0"},
        )
        old_env = EventEnvelopeV1(
            event_id=str(compute_deterministic_event_id("binance", EventType.TRADE, "BTCUSDT", "2001")),
            event_type=EventType.TRADE,
            schema_version=SCHEMA_VERSION_V1,
            provider="binance",
            symbol="BTCUSDT",
            exchange_event_time=t_old,
            ingested_at=t_new,
            sequence_id=1,
            payload={"trade_id": "2001", "price": "85000", "quantity": "1.0"},
        )
        self.assertTrue(projector.project_event(new_env))
        self.assertFalse(projector.project_event(old_env))
        self.assertEqual(projector.dropped_out_of_order_count, 1)

    def test_anomaly_detector_enforces_cooldown_suppression(self) -> None:
        detector = StatisticalAnomalyDetector(zscore_threshold=2.0, cooldown_seconds=900)
        base_now = datetime(2026, 11, 15, 3, 0, tzinfo=UTC)
        series = [100.0, 100.1, 99.9, 100.0, 100.05, 115.0]
        env1, anom1 = detector.evaluate_series("binance", "BTCUSDT", series, now_utc=base_now)
        self.assertIsNotNone(env1)
        self.assertIsNotNone(anom1)
        env2, anom2 = detector.evaluate_series(
            "binance", "BTCUSDT", series, now_utc=base_now + timedelta(minutes=5)
        )
        self.assertIsNone(env2)
        self.assertIsNone(anom2)
        self.assertEqual(detector.suppressed_alerts_count, 1)
