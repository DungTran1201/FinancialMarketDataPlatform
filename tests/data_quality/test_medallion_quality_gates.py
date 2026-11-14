"""Data Quality Gate, Silver Merge & Gold Materialization Verification (`TC-012`)."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from src.lakehouse.bronze.archiver import BronzeParquetArchiver
from src.lakehouse.gold.mart_engine import GoldLayerMartEngine
from src.lakehouse.quality.gates import DataQualityGateEngine
from src.lakehouse.silver.merge_engine import SilverLakehouseMergeEngine
from src.shared.contracts.events.market_events import (
    SCHEMA_VERSION_V1,
    EventEnvelopeV1,
    EventType,
    compute_deterministic_event_id,
)


class TestMedallionDataQualityGates(unittest.TestCase):
    """Validates blocking DQ rules, natural-key Silver deduplication, Iceberg snapshots, and Gold Decimal precision."""

    def test_dq_engine_blocks_invalid_ohlc_and_duplicate_natural_keys(self) -> None:
        dq = DataQualityGateEngine()
        bad_rows = [
            {
                "provider": "binance",
                "symbol": "BTCUSDT",
                "interval": "1m",
                "open_time": "2026-11-15T00:00:00Z",
                "close_time": "2026-11-15T00:01:00Z",
                "open_price": "100.00",
                "high_price": "99.00",  # DQ-KLINE-001 violation: high < low
                "low_price": "101.00",
                "close_price": "100.00",
                "base_volume": "-5.0",  # DQ-KLINE-003 violation: negative volume
                "quote_volume": "1000.00",
            }
        ]
        result = dq.validate_kline_dataset(bad_rows)
        self.assertFalse(result.passed)
        self.assertFalse(result.can_promote_to_gold)
        self.assertIn("DQ-KLINE-001", result.failed_rule_ids)
        self.assertIn("DQ-KLINE-003", result.failed_rule_ids)

    def test_bronze_to_silver_compaction_and_gold_decimal_precision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archiver = BronzeParquetArchiver(root)
            silver = SilverLakehouseMergeEngine(root)
            gold = GoldLayerMartEngine(root)
            dq = DataQualityGateEngine()

            t0 = datetime(2026, 11, 15, 0, 0, tzinfo=UTC)
            envelopes = []
            for idx in range(2):
                open_dt = t0 + timedelta(minutes=idx)
                eid = compute_deterministic_event_id(
                    "binance", EventType.KLINE, "BTCUSDT", open_dt.isoformat()
                )
                envelopes.append(
                    EventEnvelopeV1(
                        event_id=str(eid),
                        event_type=EventType.KLINE,
                        schema_version=SCHEMA_VERSION_V1,
                        provider="binance",
                        symbol="BTCUSDT",
                        exchange_event_time=open_dt,
                        ingested_at=open_dt,
                        sequence_id=idx + 1,
                        payload={
                            "interval": "1m",
                            "open_time": open_dt.isoformat(),
                            "close_time": (open_dt + timedelta(minutes=1)).isoformat(),
                            "open_price": "89000.12345678",
                            "high_price": "89100.12345678",
                            "low_price": "88950.12345678",
                            "close_price": "89050.12345678",
                            "base_volume": "12.50000000",
                            "quote_volume": "1112500.00000000",
                            "trade_count": 40,
                            "is_closed": True,
                        },
                    )
                )

            bronze_paths = archiver.archive_batch(envelopes)
            self.assertGreaterEqual(len(bronze_paths), 1)

            # Run Silver merge twice with overlapping files to verify natural-key idempotency
            _, rows = silver.merge_bronze_klines_to_silver(bronze_paths)
            _, rows2 = silver.merge_bronze_klines_to_silver(bronze_paths)
            self.assertEqual(len(rows), 2)
            self.assertEqual(len(rows2), 2)

            dq_res = dq.validate_kline_dataset(rows2)
            self.assertTrue(dq_res.passed)
            self.assertTrue(dq_res.can_promote_to_gold)

            snap1 = silver.compact_and_snapshot_iceberg_table(
                layer="silver", table_name="market_klines"
            )
            snap2 = silver.compact_and_snapshot_iceberg_table(
                layer="silver", table_name="market_klines"
            )
            self.assertEqual(snap2.files_after_compaction, 1)
            self.assertNotEqual(snap2.snapshot_id, snap1.snapshot_id)
            self.assertEqual(snap2.parent_snapshot_id, snap1.snapshot_id)
            manifest = json.loads(Path(snap2.metadata_manifest_path).read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(manifest["snapshots"]), 2)

            summary = gold.materialize_daily_market_summary(rows2)
            self.assertEqual(summary.row_count, 1)
            Decimal(str(summary.rows[0]["daily_return_pct"]))
