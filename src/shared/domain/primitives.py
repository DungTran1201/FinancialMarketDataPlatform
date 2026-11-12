"""Pure domain value objects and exceptions shared across bounded contexts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


class DomainError(Exception):
    """Base class for pure domain rule violations."""


class QueryRangeExceededError(DomainError):
    """Raised when a query exceeds bounded time or row limits."""


class StaleDataError(DomainError):
    """Raised when data age breaches hard staleness constraints."""


@dataclass(frozen=True, slots=True)
class InstrumentKey:
    """Value object identifying a canonical provider + symbol instrument."""

    provider: str
    symbol: str

    def __post_init__(self) -> None:
        if not self.provider or not self.provider.islower():
            raise DomainError(f"provider must be lowercase non-empty string, got '{self.provider}'")
        if not self.symbol or not self.symbol.isupper() or not self.symbol.isalnum():
            raise DomainError(f"symbol must be uppercase alphanumeric string, got '{self.symbol}'")

    @property
    def canonical_id(self) -> str:
        return f"{self.provider}:{self.symbol}"


@dataclass(frozen=True, slots=True)
class BoundedTimeRange:
    """Value object enforcing bounded start and end UTC timestamps on analytical queries."""

    start_time: datetime
    end_time: datetime
    max_span_seconds: int = 7 * 86400

    def __post_init__(self) -> None:
        if self.start_time.tzinfo is None or self.end_time.tzinfo is None:
            raise DomainError("start_time and end_time must be timezone-aware UTC datetimes")
        if self.end_time < self.start_time:
            raise DomainError("end_time must be >= start_time")
        span = (self.end_time - self.start_time).total_seconds()
        if span > self.max_span_seconds:
            raise QueryRangeExceededError(
                f"Requested window ({span:.0f}s) exceeds maximum synchronous span ({self.max_span_seconds}s)"
            )


@dataclass(frozen=True, slots=True)
class DecimalPrice:
    """Exact monetary decimal value object."""

    value: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal) or self.value.is_nan() or self.value.is_infinite():
            raise DomainError("Price must be a finite Decimal instance")
        if self.value < Decimal("0"):
            raise DomainError("Price cannot be negative")

