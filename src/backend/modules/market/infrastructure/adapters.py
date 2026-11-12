"""Market Infrastructure Adapters (Redis Hot Store & ClickHouse Fallback)."""

from __future__ import annotations

from src.backend.modules.market.domain.entities import LatestPriceQuote
from src.backend.modules.market.domain.ports import (
    MarketFallbackRepositoryPort,
    MarketHotStorePort,
)
from src.shared.domain.primitives import InstrumentKey


class InMemoryMarketHotStoreAdapter(MarketHotStorePort):
    """Deterministic adapter implementing MarketHotStorePort for scaffolding & tests."""

    def __init__(self, initial_quotes: dict[str, LatestPriceQuote] | None = None) -> None:
        self._quotes: dict[str, LatestPriceQuote] = dict(initial_quotes or {})

    async def get_latest_price(self, instrument: InstrumentKey) -> LatestPriceQuote | None:
        return self._quotes.get(instrument.canonical_id)


class InMemoryClickHouseFallbackAdapter(MarketFallbackRepositoryPort):
    """Deterministic fallback adapter implementing MarketFallbackRepositoryPort."""

    def __init__(self, fallback_quotes: dict[str, LatestPriceQuote] | None = None) -> None:
        self._quotes: dict[str, LatestPriceQuote] = dict(fallback_quotes or {})

    async def get_latest_price_fallback(
        self, instrument: InstrumentKey
    ) -> LatestPriceQuote | None:
        return self._quotes.get(instrument.canonical_id)

