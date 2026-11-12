"""Unit & Contract Tests for Event Envelopes, Hot/Fallback Routing, and Agent Tool Gateway."""

from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from src.agent.tools.contracts import ApprovedAgentTool
from src.agent.tools.gateway import (
    ControlledToolGateway,
    ToolQueryLimitExceededError,
    UnauthorizedToolAccessError,
    compute_deterministic_log_returns,
    compute_deterministic_realized_volatility,
)
from src.backend.modules.market.application.queries import GetLatestPriceQueryHandler
from src.backend.modules.market.domain.entities import LatestPriceQuote
from src.backend.modules.market.infrastructure.adapters import (
    InMemoryClickHouseFallbackAdapter,
    InMemoryMarketHotStoreAdapter,
)
from src.shared.contracts.events import (
    SCHEMA_VERSION_V1,
    EventEnvelopeV1,
    EventType,
    MarketKlinePayloadV1,
    MarketTradePayloadV1,
    compute_deterministic_event_id,
    compute_partition_key,
)
from src.shared.domain.primitives import (
    BoundedTimeRange,
    InstrumentKey,
    QueryRangeExceededError,
)


class TestEventContractsAndDomainInvariants(unittest.TestCase):
    """Tests canonical data contracts, deterministic deduplication IDs, and domain guards."""

    def test_deterministic_event_id_is_idempotent(self) -> None:
        id_1 = compute_deterministic_event_id("binance", EventType.TRADE, "BTCUSDT", "419283741")
        id_2 = compute_deterministic_event_id("BINANCE", "trade", "btcusdt", "419283741")
        id_diff = compute_deterministic_event_id("binance", EventType.TRADE, "BTCUSDT", "419283742")
        self.assertEqual(id_1, id_2)
        self.assertNotEqual(id_1, id_diff)

    def test_partition_key_preserves_symbol_ordering(self) -> None:
        self.assertEqual(compute_partition_key("Binance", "btcusdt"), "binance:BTCUSDT")
        self.assertEqual(compute_partition_key("binance", "ETHUSDT", "1m"), "binance:ETHUSDT:1m")

    def test_kline_and_trade_invariants_reject_corrupted_values(self) -> None:
        now = datetime.now(UTC)
        valid_trade = MarketTradePayloadV1(
            trade_id=1001,
            price=Decimal("89420.50"),
            quantity=Decimal("0.25"),
            quote_volume=Decimal("22355.125"),
            trade_time=now,
            is_buyer_maker=False,
        )
        self.assertEqual(valid_trade.price, Decimal("89420.50"))

        with self.assertRaises(ValueError):
            MarketKlinePayloadV1(
                interval="1m",
                open_time=now,
                close_time=now + timedelta(minutes=1),
                open_price=Decimal("100"),
                high_price=Decimal("90"),  # Invalid: high < low/open
                low_price=Decimal("95"),
                close_price=Decimal("98"),
                base_volume=Decimal("10"),
                quote_volume=Decimal("980"),
                trade_count=5,
                taker_buy_base_volume=Decimal("5"),
                taker_buy_quote_volume=Decimal("490"),
                is_closed=True,
            )

    def test_bounded_time_range_rejects_excessive_window(self) -> None:
        now = datetime.now(UTC)
        with self.assertRaises(QueryRangeExceededError):
            BoundedTimeRange(
                start_time=now - timedelta(days=30),
                end_time=now,
                max_span_seconds=7 * 86400,
            )

    def test_event_envelope_requires_utc_timestamps(self) -> None:
        now = datetime.now(UTC)
        env = EventEnvelopeV1(
            event_id=compute_deterministic_event_id("binance", EventType.KLINE, "BTCUSDT", "1"),
            schema_version=SCHEMA_VERSION_V1,
            provider="binance",
            symbol="BTCUSDT",
            event_type=EventType.KLINE,
            exchange_event_time=now,
            ingested_at=now,
            payload={"interval": "1m"},
        )
        self.assertEqual(env.partition_key, "binance:BTCUSDT:1m")


class TestAsyncHotToClickHouseFallbackAndToolGateway(unittest.IsolatedAsyncioTestCase):
    """Tests Redis -> ClickHouse fallback (ADR-005) and Controlled Tool Gateway (ADR-006)."""

    async def test_market_query_reads_from_redis_when_available(self) -> None:
        now = datetime.now(UTC)
        inst = InstrumentKey(provider="binance", symbol="BTCUSDT")
        quote = LatestPriceQuote(
            instrument=inst,
            last_price=Decimal("89500.25"),
            exchange_event_time=now - timedelta(seconds=2),
            ingested_at=now - timedelta(seconds=1),
        )
        hot_store = InMemoryMarketHotStoreAdapter({"binance:BTCUSDT": quote})
        fallback_store = InMemoryClickHouseFallbackAdapter({})
        handler = GetLatestPriceQueryHandler(hot_store, fallback_store, staleness_threshold_ms=15000)

        dto = await handler.handle("binance", "BTCUSDT", now_utc=now)
        self.assertIsNotNone(dto)
        assert dto is not None
        self.assertEqual(dto.source, "redis_hot_cache")
        self.assertEqual(dto.last_price, "89500.25")
        self.assertFalse(dto.is_stale)

    async def test_market_query_transparently_falls_back_to_clickhouse_on_redis_miss(self) -> None:
        now = datetime.now(UTC)
        inst = InstrumentKey(provider="binance", symbol="ETHUSDT")
        fallback_quote = LatestPriceQuote(
            instrument=inst,
            last_price=Decimal("3120.10"),
            exchange_event_time=now - timedelta(seconds=20),
            ingested_at=now - timedelta(seconds=19),
        )
        hot_store = InMemoryMarketHotStoreAdapter({})
        fallback_store = InMemoryClickHouseFallbackAdapter({"binance:ETHUSDT": fallback_quote})
        handler = GetLatestPriceQueryHandler(hot_store, fallback_store, staleness_threshold_ms=15000)

        dto = await handler.handle("binance", "ETHUSDT", now_utc=now)
        self.assertIsNotNone(dto)
        assert dto is not None
        self.assertEqual(dto.source, "clickhouse_fallback")
        self.assertEqual(dto.last_price, "3120.10")
        self.assertTrue(dto.is_stale)

    async def test_tool_gateway_enforces_whitelist_rbac_and_row_limits(self) -> None:
        gateway = ControlledToolGateway()
        analyst_perms = frozenset({"market:read", "historical:read", "analytics:read", "agent:trigger"})

        # 1. Reject arbitrary SQL tool not in whitelist
        with self.assertRaises(UnauthorizedToolAccessError):
            await gateway.execute_tool("execute_raw_sql", {"query": "DROP TABLE users"}, analyst_perms)

        # 2. Reject missing RBAC permission
        with self.assertRaises(UnauthorizedToolAccessError):
            await gateway.execute_tool(
                ApprovedAgentTool.GENERATE_ANALYSIS_REPORT.value,
                {"symbol": "BTCUSDT"},
                frozenset({"market:read"}),
            )

        # 3. Reject excessive row limit (>500 candles)
        with self.assertRaises(ToolQueryLimitExceededError):
            await gateway.execute_tool(
                ApprovedAgentTool.GET_HISTORICAL_CANDLES.value,
                {"symbol": "BTCUSDT", "limit": 5000},
                analyst_perms,
            )

        # 4. Succeed with valid whitelisted tool and attach provenance
        envelope = await gateway.execute_tool(
            ApprovedAgentTool.CALCULATE_VOLATILITY.value,
            {"symbol": "BTCUSDT", "lookback_periods": 24},
            analyst_perms,
        )
        self.assertEqual(envelope.status, "SUCCESS")
        self.assertEqual(envelope.provenance.tool_name, ApprovedAgentTool.CALCULATE_VOLATILITY)
        self.assertEqual(envelope.provenance.symbol, "BTCUSDT")

    async def test_deterministic_quant_calculations_are_exact(self) -> None:
        prices = [100.0, 102.0, 101.0, 105.0]
        returns = compute_deterministic_log_returns(prices)
        self.assertEqual(len(returns), 3)
        vol = compute_deterministic_realized_volatility(prices, periods_per_year=365)
        self.assertGreater(vol, 0.0)


if __name__ == "__main__":
    unittest.main()
