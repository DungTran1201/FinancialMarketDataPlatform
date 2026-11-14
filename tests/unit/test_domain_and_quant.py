"""Unit Tests for Shared Domain Primitives, Deterministic Quant Math & Ingestion Helpers."""

from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from src.ingestion.application.rate_limiter import TokenBucketRateLimiter
from src.ingestion.infrastructure.watermark_store import IngestionWatermarkStore
from src.shared.domain.primitives import (
    BoundedTimeRange,
    DecimalPrice,
    DomainError,
    InstrumentKey,
    QueryRangeExceededError,
)
from src.shared.domain.quant import (
    compute_deterministic_log_returns,
    compute_deterministic_pearson_correlation,
    compute_deterministic_realized_volatility,
)


class TestSharedDomainAndQuant(unittest.TestCase):
    """Verifies pure domain invariants and deterministic quant computations."""

    def test_instrument_key_enforces_lowercase_provider_and_uppercase_symbol(self) -> None:
        key = InstrumentKey(provider="binance", symbol="BTCUSDT")
        self.assertEqual(key.provider, "binance")
        self.assertEqual(key.symbol, "BTCUSDT")
        self.assertEqual(key.canonical_id, "binance:BTCUSDT")

        with self.assertRaises(DomainError):
            InstrumentKey(provider="Binance", symbol="BTCUSDT")

    def test_decimal_price_enforces_positive_fixed_point(self) -> None:
        p = DecimalPrice(Decimal("89500.125"))
        self.assertEqual(p.value, Decimal("89500.125"))
        with self.assertRaises(DomainError):
            DecimalPrice(Decimal("-1.0"))

    def test_bounded_time_range_rejects_inverted_and_oversized_windows(self) -> None:
        end = datetime(2026, 11, 15, 12, 0, tzinfo=UTC)
        start = end - timedelta(days=2)
        BoundedTimeRange(start_time=start, end_time=end, max_span_seconds=7 * 86400)

        with self.assertRaises(QueryRangeExceededError):
            BoundedTimeRange(
                start_time=end - timedelta(days=10),
                end_time=end,
                max_span_seconds=7 * 86400,
            )

    def test_quant_math_returns_volatility_and_pearson_correlation(self) -> None:
        returns = compute_deterministic_log_returns([100.0, 105.0, 102.0, 108.0])
        self.assertEqual(len(returns), 3)
        vol = compute_deterministic_realized_volatility([100.0, 102.0, 101.0, 104.0])
        self.assertGreater(vol, 0.0)
        corr = compute_deterministic_pearson_correlation([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
        self.assertAlmostEqual(corr, 1.0, places=6)

    def test_token_bucket_rate_limiter_and_sqlite_watermark_store(self) -> None:
        limiter = TokenBucketRateLimiter(max_weight_per_minute=100, safety_ratio=0.8)
        self.assertEqual(limiter.safe_weight_ceiling, 80)

        with tempfile.TemporaryDirectory() as tmp:
            store = IngestionWatermarkStore(db_path=Path(tmp) / "watermarks.db")
            try:
                ts = datetime(2026, 11, 15, 1, 0, tzinfo=UTC)
                rec = store.upsert_watermark(
                    provider="binance",
                    symbol="BTCUSDT",
                    interval="1m",
                    last_open_time=ts,
                    status="SYNCED",
                )
                self.assertEqual(rec.status, "SYNCED")
                loaded = store.get_watermark("binance", "BTCUSDT", "1m")
                self.assertIsNotNone(loaded)
                assert loaded is not None
                self.assertEqual(loaded.last_open_time, ts)
                self.assertEqual(len(store.list_watermarks()), 1)
            finally:
                store.close()
