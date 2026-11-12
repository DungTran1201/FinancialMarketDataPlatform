"""Platform Configuration domain ports (Pure Domain Layer)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class MonitoredInstrumentConfig:
    """Configuration entity for an ingested trading pair."""

    provider: str
    symbol: str
    enabled_streams: tuple[str, ...]
    is_active: bool = True


class PlatformConfigRepositoryPort(Protocol):
    """Port for managing monitored symbols and stream subscriptions in PostgreSQL."""

    async def list_active_instruments(self) -> list[MonitoredInstrumentConfig]: ...

