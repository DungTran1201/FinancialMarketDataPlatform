"""Data Catalog domain ports (Pure Domain Layer)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.shared.domain.primitives import InstrumentKey


@dataclass(frozen=True, slots=True)
class DataFreshnessReport:
    """Domain entity summarizing end-to-end data freshness across hot and OLAP paths."""

    instrument: InstrumentKey
    hot_redis_lag_ms: int
    clickhouse_lag_ms: int
    is_healthy: bool


class DataCatalogRepositoryPort(Protocol):
    """Port for querying monitored instruments and data freshness."""

    async def get_freshness(self, instrument: InstrumentKey) -> DataFreshnessReport: ...

