"""Market Application Query Handlers implementing Redis -> ClickHouse fallback (CQRS Read Side)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from src.backend.modules.market.domain.entities import LatestPriceQuote
from src.backend.modules.market.domain.ports import (
    MarketFallbackRepositoryPort,
    MarketHotStorePort,
)
from src.shared.domain.primitives import InstrumentKey


@dataclass(frozen=True, slots=True)
class LatestPriceReadDTO:
    """Application layer read DTO including data source and staleness metadata."""

    provider: str
    symbol: str
    last_price: str
    exchange_event_time: str
    source: str
    age_ms: int
    is_stale: bool


class GetLatestPriceQueryHandler:
    """Executes hot price read from Redis with transparent fallback to ClickHouse (ADR-005)."""

    def __init__(
        self,
        hot_store: MarketHotStorePort,
        fallback_repo: MarketFallbackRepositoryPort,
        staleness_threshold_ms: int = 15000,
    ) -> None:
        self._hot_store = hot_store
        self._fallback_repo = fallback_repo
        self._staleness_threshold_ms = staleness_threshold_ms

    async def handle(
        self,
        provider: str,
        symbol: str,
        now_utc: datetime | None = None,
    ) -> LatestPriceReadDTO | None:
        instrument = InstrumentKey(provider=provider.lower(), symbol=symbol.upper())
        reference_now = now_utc or datetime.now(UTC)

        quote: LatestPriceQuote | None = None
        source = "redis_hot_cache"

        try:
            quote = await self._hot_store.get_latest_price(instrument)
        except Exception:
            quote = None

        if quote is None:
            source = "clickhouse_fallback"
            quote = await self._fallback_repo.get_latest_price_fallback(instrument)

        if quote is None:
            return None

        return LatestPriceReadDTO(
            provider=instrument.provider,
            symbol=instrument.symbol,
            last_price=str(quote.last_price),
            exchange_event_time=quote.exchange_event_time.isoformat(),
            source=source,
            age_ms=quote.compute_age_ms(reference_now),
            is_stale=quote.is_stale(reference_now, self._staleness_threshold_ms),
        )

