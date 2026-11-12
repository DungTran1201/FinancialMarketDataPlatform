"""Historical Data domain ports (Pure Domain Layer)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from src.shared.domain.primitives import BoundedTimeRange, InstrumentKey


@dataclass(frozen=True, slots=True)
class HistoricalCandleEntity:
    """Domain entity representing an OHLCV candle."""

    instrument: InstrumentKey
    interval: str
    open_time: datetime
    close_time: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    base_volume: Decimal
    quote_volume: Decimal
    trade_count: int


class HistoricalKlineRepositoryPort(Protocol):
    """Port for bounded historical kline queries backed by ClickHouse."""

    async def query_klines(
        self,
        instrument: InstrumentKey,
        interval: str,
        time_range: BoundedTimeRange,
        limit: int = 500,
    ) -> list[HistoricalCandleEntity]: ...

