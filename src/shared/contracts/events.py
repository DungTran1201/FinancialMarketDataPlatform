"""Canonical Event Contracts & Deterministic Event ID Generation (EventEnvelopeV1)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

PLATFORM_EVENT_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
SCHEMA_VERSION_V1 = "1.0.0"


class EventType(StrEnum):
    """Canonical platform event types."""

    TRADE = "trade"
    KLINE = "kline"
    TICKER = "ticker"
    ORDER_BOOK = "order_book"
    ANOMALY = "anomaly"


class KafkaTopic(StrEnum):
    """Approved versioned Kafka topic names."""

    TRADES_V1 = "market.raw.trades.v1"
    KLINES_V1 = "market.raw.klines.v1"
    TICKERS_V1 = "market.raw.tickers.v1"
    ORDERBOOK_V1 = "market.raw.orderbook.v1"
    ANOMALIES_V1 = "market.anomalies.v1"
    DLQ_V1 = "market.dlq.v1"


def compute_deterministic_event_id(
    provider: str,
    event_type: EventType | str,
    symbol: str,
    natural_key: str,
) -> str:
    """Compute a deterministic UUIDv5 for idempotent deduplication across sinks."""
    canonical_name = f"{provider.lower()}:{str(event_type).lower()}:{symbol.upper()}:{natural_key}"
    return str(uuid.uuid5(PLATFORM_EVENT_NAMESPACE, canonical_name))


def compute_partition_key(provider: str, symbol: str, interval: str | None = None) -> str:
    """Return the Kafka partition key preserving per-symbol ordering."""
    base = f"{provider.lower()}:{symbol.upper()}"
    return f"{base}:{interval}" if interval else base


@dataclass(frozen=True, slots=True)
class MarketTradePayloadV1:
    """Canonical trade payload with exact Decimal financial representations."""

    trade_id: int
    price: Decimal
    quantity: Decimal
    quote_volume: Decimal
    trade_time: datetime
    is_buyer_maker: bool
    buyer_order_id: int | None = None
    seller_order_id: int | None = None

    def __post_init__(self) -> None:
        if self.trade_id <= 0:
            raise ValueError("trade_id must be positive")
        if self.price <= Decimal("0") or self.quantity <= Decimal("0"):
            raise ValueError("price and quantity must be strictly positive Decimals")


@dataclass(frozen=True, slots=True)
class MarketKlinePayloadV1:
    """Canonical OHLCV kline payload enforcing financial candle invariants."""

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
    taker_buy_base_volume: Decimal
    taker_buy_quote_volume: Decimal
    is_closed: bool

    def __post_init__(self) -> None:
        if self.high_price < self.low_price:
            raise ValueError("Kline invariant violated: high_price < low_price")
        if self.high_price < self.open_price or self.high_price < self.close_price:
            raise ValueError("Kline invariant violated: high_price below open/close")
        if self.low_price > self.open_price or self.low_price > self.close_price:
            raise ValueError("Kline invariant violated: low_price above open/close")
        if self.base_volume < Decimal("0") or self.quote_volume < Decimal("0"):
            raise ValueError("Kline volume cannot be negative")


@dataclass(frozen=True, slots=True)
class EventEnvelopeV1:
    """Canonical versioned event envelope published to Apache Kafka."""

    event_id: str
    schema_version: str
    provider: str
    symbol: str
    event_type: EventType
    exchange_event_time: datetime
    ingested_at: datetime
    payload: dict[str, Any]
    sequence_id: int | None = None

    def __post_init__(self) -> None:
        if not self.provider or not self.symbol:
            raise ValueError("provider and symbol are required on EventEnvelopeV1")
        if self.exchange_event_time.tzinfo is None or self.ingested_at.tzinfo is None:
            raise ValueError("All timestamps on EventEnvelopeV1 must be timezone-aware UTC")

    @property
    def partition_key(self) -> str:
        interval = self.payload.get("interval") if self.event_type == EventType.KLINE else None
        return compute_partition_key(self.provider, self.symbol, interval)


@dataclass(frozen=True, slots=True)
class DeadLetterEnvelopeV1:
    """Dead-letter contract for malformed or unparseable upstream payloads."""

    dlq_id: str
    source_provider: str
    source_stream: str
    error_type: str
    error_message: str
    raw_payload: str
    failed_at: datetime = datetime.now(UTC)

