"""Kafka Partitioned Streaming Broker & Confluent Kafka Production Adapter (Stage 4)."""

from __future__ import annotations

import json
import time
from collections import defaultdict, deque
from datetime import UTC, datetime
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
        now_epoch = time.time()
        self._topics[topic].append(
            {
                "topic": topic,
                "partition": partition,
                "offset": offset,
                "key": event.partition_key,
                "event_id": ev_id_str,
                "published_at_utc": datetime.now(UTC).isoformat(),
                "published_epoch_s": now_epoch,
                "envelope": event,
            }
        )
        self._record_activity("publish", topic, 1, now_epoch)
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
        now_epoch = time.time()
        dlq_topic = KafkaTopic.DLQ_V1.value
        self._topics[dlq_topic].append(
            {
                "topic": dlq_topic,
                "partition": 0,
                "offset": len(self._topics[dlq_topic]),
                "key": dlq_event.source_provider,
                "event_id": str(dlq_event.dlq_id),
                "published_at_utc": datetime.now(UTC).isoformat(),
                "published_epoch_s": now_epoch,
                "dlq": dlq_event,
            }
        )
        self._record_activity("dlq", dlq_topic, 1, now_epoch)

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
        prev_offset = self._committed_offsets[(consumer_group, topic)]
        new_offset = min(total, prev_offset + count)
        self._committed_offsets[(consumer_group, topic)] = new_offset
        delta = max(0, new_offset - prev_offset)
        if delta > 0:
            self._record_activity("consume", topic, delta, time.time())
        if self._state_path is not None:
            self._persist_offsets_to_disk()
        return new_offset

    def commit_up_to_latest(self, consumer_group: str, topic: str) -> int:
        """Commit all currently published messages on `topic` for `consumer_group`."""
        lag = self.get_topic_lag(consumer_group, topic)
        return self.commit_offsets(consumer_group, topic, lag)

    def _record_activity(self, kind: str, topic: str, count: int, epoch_s: float) -> None:
        log = getattr(self, "_activity_log", None)
        if log is None:
            log = deque(maxlen=5000)
            self._activity_log = log
        log.append((epoch_s, kind, topic, count))

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

    def get_cluster_snapshot(
        self,
        selected_topic: str | None = None,
        window_seconds: float | None = 300.0,
    ) -> dict[str, Any]:
        """Return honest read-only topology, partitions, offsets, lag, and publish/consume activity."""
        canonical_cgs: dict[str, list[str]] = {
            KafkaTopic.TRADES_V1.value: [
                "cg.hot.redis.v1",
                "cg.analytics.clickhouse.v1",
                "cg.lakehouse.bronze.v1",
            ],
            KafkaTopic.KLINES_V1.value: [
                "cg.hot.redis.v1",
                "cg.analytics.clickhouse.v1",
                "cg.lakehouse.bronze.v1",
            ],
            KafkaTopic.TICKERS_V1.value: [
                "cg.hot.redis.v1",
                "cg.analytics.clickhouse.v1",
                "cg.lakehouse.bronze.v1",
            ],
            KafkaTopic.ORDERBOOK_V1.value: [
                "cg.hot.redis.v1",
                "cg.analytics.clickhouse.v1",
                "cg.lakehouse.bronze.v1",
            ],
            KafkaTopic.ANOMALIES_V1.value: ["cg.anomaly.detector.v1", "cg.lakehouse.bronze.v1"],
            KafkaTopic.DLQ_V1.value: ["cg.dlq.inspector.v1"],
        }

        all_topics = sorted({t.value for t in KafkaTopic} | set(self._topics.keys()))
        active_topic = selected_topic if selected_topic in all_topics else KafkaTopic.TRADES_V1.value
        topics_summary: list[dict[str, Any]] = []
        total_messages_all = 0
        total_lag_all = 0

        for tp in all_topics:
            records = self._topics.get(tp, [])
            total_messages = len(records)
            total_messages_all += total_messages

            cgs_for_topic = list(canonical_cgs.get(tp, []))
            for cg_key, tp_key in self._committed_offsets:
                if tp_key == tp and cg_key not in cgs_for_topic:
                    cgs_for_topic.append(cg_key)

            cg_statuses: list[dict[str, Any]] = []
            topic_lag_sum = 0
            for cg in cgs_for_topic:
                committed = self._committed_offsets.get((cg, tp), 0)
                lag = max(0, total_messages - committed)
                topic_lag_sum += lag
                cg_statuses.append(
                    {
                        "consumer_group": cg,
                        "committed_offset": committed,
                        "total_messages": total_messages,
                        "lag": lag,
                        "status": "LAGGING" if lag > 0 else ("CAUGHT_UP" if total_messages > 0 else "IDLE"),
                    }
                )
            total_lag_all += topic_lag_sum

            part_buckets: dict[int, list[dict[str, Any]]] = {p: [] for p in range(self._num_partitions)}
            for rec in records:
                p_id = int(rec.get("partition", 0))
                part_buckets.setdefault(p_id, []).append(rec)

            partitions_info = []
            for p_id in sorted(part_buckets.keys()):
                p_recs = part_buckets[p_id]
                partitions_info.append(
                    {
                        "partition_id": p_id,
                        "message_count": len(p_recs),
                        "latest_offset": p_recs[-1]["offset"] if p_recs else None,
                        "recent_messages": [
                            {
                                "offset": r["offset"],
                                "event_id": (
                                    r.get("event_id") or str(r["envelope"].event_id)
                                    if "envelope" in r
                                    else r.get("event_id", "")
                                ),
                                "key": r.get("key", ""),
                                "symbol": r["envelope"].symbol if "envelope" in r else r.get("key", ""),
                                "event_type": r["envelope"].event_type.value if "envelope" in r else "dlq",
                                "published_at_utc": r.get("published_at_utc"),
                            }
                            for r in p_recs[-8:]
                        ],
                    }
                )

            topics_summary.append(
                {
                    "topic": tp,
                    "partition_count": self._num_partitions,
                    "total_messages": total_messages,
                    "total_lag": topic_lag_sum,
                    "partitions": partitions_info,
                    "consumer_groups": cg_statuses,
                }
            )

        selected_detail = next((t for t in topics_summary if t["topic"] == active_topic), topics_summary[0])

        # Build publish / consume timeseries from activity log
        act_log: deque[tuple[float, str, str, int]] = getattr(self, "_activity_log", deque())
        now = time.time()
        cutoff = (now - window_seconds) if window_seconds is not None else None
        relevant = [item for item in act_log if cutoff is None or item[0] >= cutoff]
        timeseries: list[dict[str, Any]] = []
        if relevant:
            t_min = relevant[0][0]
            t_max = max(relevant[-1][0], t_min + 1.0)
            num_buckets = 12
            width = max(0.05, (t_max - t_min) / num_buckets)
            for idx in range(num_buckets):
                b_start = t_min + idx * width
                b_end = t_min + (idx + 1) * width + (1e-6 if idx == num_buckets - 1 else 0.0)
                pub_c = sum(cnt for ts, kind, _tp, cnt in relevant if kind == "publish" and b_start <= ts < b_end)
                con_c = sum(cnt for ts, kind, _tp, cnt in relevant if kind == "consume" and b_start <= ts < b_end)
                dlq_c = sum(cnt for ts, kind, _tp, cnt in relevant if kind == "dlq" and b_start <= ts < b_end)
                if pub_c or con_c or dlq_c:
                    timeseries.append(
                        {
                            "label": datetime.fromtimestamp(b_end, tz=UTC).strftime("%H:%M:%S"),
                            "published": pub_c,
                            "consumed": con_c,
                            "dlq": dlq_c,
                        }
                    )

        return {
            "engine_mode": "LIVE_CONFLUENT_ADAPTER"
            if self._confluent_adapter is not None
            else "IN_PROCESS_PARTITIONED_BROKER",
            "num_partitions_per_topic": self._num_partitions,
            "total_messages_all_topics": total_messages_all,
            "total_lag_all_topics": total_lag_all,
            "total_dlq_messages": len(self._dlq),
            "duplicate_drops_count": self._duplicate_drops,
            "selected_topic": active_topic,
            "topics": topics_summary,
            "selected_topic_detail": selected_detail,
            "dlq_recent": [
                {
                    "dlq_id": str(d.dlq_id),
                    "source_provider": d.source_provider,
                    "source_stream": d.source_stream,
                    "error_type": d.error_type,
                    "error_message": d.error_message,
                    "failed_at": d.failed_at.isoformat(),
                }
                for d in self._dlq[-20:]
            ],
            "publish_consume_timeseries": timeseries,
        }
