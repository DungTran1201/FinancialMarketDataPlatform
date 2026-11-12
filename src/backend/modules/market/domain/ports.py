"""Market domain ports (Hexagonal Architecture Interfaces)."""

from __future__ import annotations

from typing import Protocol

from src.backend.modules.market.domain.entities import LatestPriceQuote
from src.shared.domain.primitives import InstrumentKey


class MarketHotStorePort(Protocol):
    """Port for sub-15ms latest price and snapshot reads from Redis."""

    async def get_latest_price(self, instrument: InstrumentKey) -> LatestPriceQuote | None: ...


class MarketFallbackRepositoryPort(Protocol):
    """Port for bounded ClickHouse fallback when Redis misses or is unavailable."""

    async def get_latest_price_fallback(
        self, instrument: InstrumentKey
    ) -> LatestPriceQuote | None: ...

