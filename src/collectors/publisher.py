"""Partitioned Event Streaming Bus & Dead-Letter Router (Plane A: Kafka Backbone)."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from src.collectors.normalizer import BinancePayloadNormalizer
from src.collectors.ports import EventPublisherPort, HistoricalCollectorPort
from src.shared.contracts.events import (
    DeadLetterEnvelopeV1,
    EventEnvelopeV1,
    EventType,
    KafkaTopic,
)


class PartitionedEventStreamingBroker(EventPublisherPort):
    """Deterministic partitioned event bus implementing Kafka topic routing, offsets & DLQ."""

    def __init__(self, num_partitions: int = 6) -> None:
        self._num_partitions = num_partitions
        self._topics: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._dlq: list[DeadLetterEnvelopeV1] = []
        self._committed_offsets: dict[tuple[str, str], int] = defaultdict(int)

    @staticmethod
    def resolve_topic_for_event(event: EventEnvelopeV1) -> str:
        mapping = {
            EventType.TRADE: KafkaTopic.TRADES_V1.value,
            EventType.KLINE: KafkaTopic.KLINES_V1.value,
            EventType.TICKER: KafkaTopic.TICKERS_V1.value,
            EventType.ORDER_BOOK: KafkaTopic.ORDERBOOK_V1.value,
            EventType.ANOMALY: KafkaTopic.ANOMALIES_V1.value,
        }
        return mapping.get(event.event_type, KafkaTopic.TRADES_V1.value)

    async def publish_event(self, topic: str, event: EventEnvelopeV1) -> int:
        partition = hash(event.partition_key) % self._num_partitions
        offset = len(self._topics[topic])
        self._topics[topic].append(
            {
                "topic": topic,
                "partition": partition,
                "offset": offset,
                "key": event.partition_key,
                "envelope": event,
            }
        )
        return partition

    async def publish_dlq(self, dlq_event: DeadLetterEnvelopeV1) -> None:
        self._dlq.append(dlq_event)
        self._topics[KafkaTopic.DLQ_V1.value].append(
            {
                "topic": KafkaTopic.DLQ_V1.value,
                "partition": 0,
                "offset": len(self._topics[KafkaTopic.DLQ_V1.value]),
                "key": dlq_event.source_provider,
                "dlq": dlq_event,
            }
        )

    def poll_topic(
        self,
        consumer_group: str,
        topic: str,
        max_records: int = 500,
    ) -> list[EventEnvelopeV1]:
        """Poll uncommitted events for a consumer group in strict offset order."""
        records = self._topics.get(topic, [])
        start_offset = self._committed_offsets[(consumer_group, topic)]
        batch = records[start_offset : start_offset + max_records]
        return [item["envelope"] for item in batch if "envelope" in item]

    def commit_offsets(self, consumer_group: str, topic: str, count: int) -> int:
        """Advance committed offset for `(consumer_group, topic)` after sink persistence."""
        self._committed_offsets[(consumer_group, topic)] += count
        return self._committed_offsets[(consumer_group, topic)]

    def get_topic_lag(self, consumer_group: str, topic: str) -> int:
        total = len(self._topics.get(topic, []))
        committed = self._committed_offsets.get((consumer_group, topic), 0)
        return max(0, total - committed)

    @property
    def dlq_events(self) -> tuple[DeadLetterEnvelopeV1, ...]:
        return tuple(self._dlq)


class SimulatedExchangeHistoricalCollector(HistoricalCollectorPort):
    """MOCKED External Exchange Transport Adapter for offline/deterministic REST backfills.

    Note: The normalization, contract validation, and watermark progression are 100% real;
    only the external network HTTP response from `https://api.binance.com/api/v3/klines`
    is mocked when running without external exchange connectivity.
    """

    def __init__(self, normalizer: BinancePayloadNormalizer | None = None) -> None:
        self._normalizer = normalizer or BinancePayloadNormalizer()

    async def fetch_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> list[EventEnvelopeV1]:
        step = timedelta(minutes=1 if interval == "1m" else 60)
        cursor = start_time.astimezone(UTC)
        end_utc = end_time.astimezone(UTC)
        base_price = Decimal("89000.00") if "BTC" in symbol.upper() else Decimal("3100.00")
        events: list[EventEnvelopeV1] = []
        idx = 0

        while cursor < end_utc and len(events) < min(limit, 1000):
            next_close = cursor + step
            delta = Decimal(str(((idx % 7) - 3) * 15))
            open_p = base_price + delta
            high_p = open_p + Decimal("45.50")
            low_p = open_p - Decimal("30.25")
            close_p = open_p + Decimal("12.75")
            raw_msg = {
                "e": "kline",
                "E": int(next_close.timestamp() * 1000),
                "s": symbol.upper(),
                "k": {
                    "t": int(cursor.timestamp() * 1000),
                    "T": int(next_close.timestamp() * 1000),
                    "s": symbol.upper(),
                    "i": interval,
                    "o": str(open_p),
                    "h": str(high_p),
                    "l": str(low_p),
                    "c": str(close_p),
                    "v": "18.50000000",
                    "q": str(close_p * Decimal("18.5")),
                    "n": 142,
                    "x": True,
                    "V": "9.25000000",
                    "Q": str(close_p * Decimal("9.25")),
                },
            }
            events.append(self._normalizer.normalize_ws_message(raw_msg, ingested_at=next_close))
            cursor = next_close
            idx += 1

        return events
