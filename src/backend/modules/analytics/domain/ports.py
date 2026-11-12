"""Analytics domain ports (Pure Domain Layer)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from src.shared.domain.primitives import InstrumentKey


@dataclass(frozen=True, slots=True)
class MarketStatisticsSummary:
    """Domain value object for aggregated symbol statistics."""

    instrument: InstrumentKey
    window: str
    vwap: Decimal
    realized_volatility: Decimal
    total_base_volume: Decimal
    total_quote_volume: Decimal
    trade_count: int


class AnalyticsQueryRepositoryPort(Protocol):
    """Port for querying ClickHouse Materialized Views & analytical marts."""

    async def get_market_statistics(
        self,
        instrument: InstrumentKey,
        window: str,
    ) -> MarketStatisticsSummary | None: ...

