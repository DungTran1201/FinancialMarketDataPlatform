"""Collector ports & provider normalization interfaces (Plane A: Data Plane)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from src.shared.contracts.events import DeadLetterEnvelopeV1, EventEnvelopeV1


class PayloadNormalizerPort(Protocol):
    """Port for translating provider-specific payloads into canonical EventEnvelopeV1."""

    @property
    def provider_name(self) -> str: ...

    def normalize_ws_message(
        self,
        raw_message: dict[str, Any],
        ingested_at: datetime,
    ) -> EventEnvelopeV1: ...


class EventPublisherPort(Protocol):
    """Port for publishing validated canonical events and routing dead letters."""

    async def publish_event(self, topic: str, event: EventEnvelopeV1) -> None: ...

    async def publish_dlq(self, dlq_event: DeadLetterEnvelopeV1) -> None: ...


class HistoricalCollectorPort(Protocol):
    """Port for paginated historical market data collection (e.g., Binance REST API)."""

    async def fetch_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> list[EventEnvelopeV1]: ...

