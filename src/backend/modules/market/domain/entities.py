"""Market domain entities & value objects (Pure Domain Layer — Zero Framework Imports)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.shared.domain.primitives import InstrumentKey


@dataclass(frozen=True, slots=True)
class LatestPriceQuote:
    """Pure domain entity representing the latest market price for an instrument."""

    instrument: InstrumentKey
    last_price: Decimal
    exchange_event_time: datetime
    ingested_at: datetime

    def compute_age_ms(self, reference_now: datetime) -> int:
        """Compute data age in milliseconds relative to reference_now."""
        delta = reference_now - self.exchange_event_time
        return max(0, int(delta.total_seconds() * 1000))

    def is_stale(self, reference_now: datetime, threshold_ms: int = 15000) -> bool:
        """Return True if data age exceeds the freshness threshold."""
        return self.compute_age_ms(reference_now) > threshold_ms

