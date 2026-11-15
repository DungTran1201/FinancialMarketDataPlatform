"""Kafka Partitioned Streaming Broker & Confluent Kafka Production Adapter (Stage 4)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.shared.contracts.events.market_events import (
    DeadLetterEnvelopeV1,
    EventEnvelopeV1,
    EventType,
    KafkaTopic,
)


class ConfluentKafkaStreamingAdapter:
    """Real Apache Kafka Producer & Consumer adapter using `confluent_kafka` (`acks=all`, idempotent)."""

    def __init__(self, bootstrap_servers: str = "localhost:9092") -> None:
        self.bootstrap_servers = bootstrap_servers
        self._producer: Any = None

    def get_producer_config(self) -> dict[str, Any]:
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "acks": "all",
            "enable.idempotence": True,
            "max.in.flight.requests.per.connection": 5,
            "retries": 5,
            "linger.ms": 5,
        }

    @staticmethod
    def get_consumer_config(bootstrap_servers: str, consumer_group: str) -> dict[str, Any]:
        return {
            "bootstrap.servers": bootstrap_servers,
            "group.id": consumer_group,
            "enable.auto.commit": False,
            "auto.offset.reset": "earliest",
            "isolation.level": "read_committed",
        }

    def publish_serialized(self, topic: str, key: str, value_json: str, partition: int | None = None) -> bool:
        """Publish to a live Kafka broker via `confluent_kafka.Producer` when connected."""
        try:
            from confluent_kafka import Producer

            if self._producer is None:
                self._producer = Producer(self.get_producer_config())
            kwargs: dict[str, Any] = {"topic": topic, "key": key.encode("utf-8"), "value": value_json.encode("utf-8")}
            if partition is not None:
                kwargs["partition"] = partition
            self._producer.produce(**kwargs)
            self._producer.poll(0)
            return True
        except Exception:
            return False


class PartitionedEventStreamingBroker:
    """Partitioned event streaming broker enforcing producer idempotency (`event_id` dedup),
    6-partition key hashing, manual consumer-group offset commits, and optional Confluent Kafka / disk persistence.
    """

    def __init__(
        self,
        num_partitions: int = 6,
        state_path: Path | str | None = None,
        confluent_adapter: ConfluentKafkaStreamingAdapter | None = None,
        deduplicate_events: bool = False,
    ) -> None:
        self._num_partitions = num_partitions
        self._topics: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._seen_event_ids: dict[str, set[str]] = defaultdict(set)
        self._duplicate_drops: int = 0
        self._dlq: list[DeadLetterEnvelopeV1] = []
        self._committed_offsets: dict[tuple[str, str], int] = defaultdict(int)
        self._state_path = Path(state_path) if state_path else None
        self._confluent_adapter = confluent_adapter
        self._deduplicate_events = deduplicate_events

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

    async def publish_event(
        self, topic: str, event: EventEnvelopeV1, deduplicate: bool | None = None
    ) -> int:
        """Publish event with optional idempotent `event_id` deduplication (`enable.idempotence=true` semantics)."""
        partition = hash(event.partition_key) % self._num_partitions
        should_dedup = self._deduplicate_events if deduplicate is None else deduplicate
        ev_id_str = str(event.event_id)
        if should_dedup and ev_id_str in self._seen_event_ids[topic]:
            self._duplicate_drops += 1
            return partition

        self._seen_event_ids[topic].add(ev_id_str)
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
        if self._confluent_adapter is not None:
            self._confluent_adapter.publish_serialized(
                topic=topic,
                key=event.partition_key,
                value_json=json.dumps(event.payload, default=str),
                partition=partition,
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
        """Poll uncommitted events for a consumer group in strict offset order without auto-committing."""
        records = self._topics.get(topic, [])
        start_offset = self._committed_offsets[(consumer_group, topic)]
        batch = records[start_offset : start_offset + max_records]
        return [item["envelope"] for item in batch if "envelope" in item]

    def commit_offsets(self, consumer_group: str, topic: str, count: int) -> int:
        """Advance committed offset for `(consumer_group, topic)` ONLY AFTER sink persistence succeeds."""
        if count < 0:
            raise ValueError("Offset commit count must be non-negative")
        total = len(self._topics.get(topic, []))
        self._committed_offsets[(consumer_group, topic)] = min(
            total, self._committed_offsets[(consumer_group, topic)] + count
        )
        if self._state_path is not None:
            self._persist_offsets_to_disk()
        return self._committed_offsets[(consumer_group, topic)]

    def get_topic_lag(self, consumer_group: str, topic: str) -> int:
        total = len(self._topics.get(topic, []))
        committed = self._committed_offsets.get((consumer_group, topic), 0)
        return max(0, total - committed)

    def _persist_offsets_to_disk(self) -> None:
        assert self._state_path is not None
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        serialized = {
            f"{cg}::{tp}": off for (cg, tp), off in self._committed_offsets.items()
        }
        self._state_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")

    @property
    def dlq_events(self) -> tuple[DeadLetterEnvelopeV1, ...]:
        return tuple(self._dlq)

    @property
    def duplicate_drops_count(self) -> int:
        return self._duplicate_drops
