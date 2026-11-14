"""Kafka consumer group constants, topic routing specs, and streaming ports."""

from __future__ import annotations

from typing import Any, Protocol

from src.shared.contracts.events.market_events import DeadLetterEnvelopeV1, EventEnvelopeV1, KafkaTopic

CG_HOT_REDIS = "cg.hot.redis.v1"
CG_ANALYTICS_CH = "cg.analytics.clickhouse.v1"
CG_LAKEHOUSE_BRONZE = "cg.lakehouse.bronze.v1"
CG_ANOMALY_DETECTOR = "cg.anomaly.detector.v1"

ALL_CANONICAL_TOPICS: tuple[KafkaTopic, ...] = (
    KafkaTopic.TRADES_V1,
    KafkaTopic.KLINES_V1,
    KafkaTopic.TICKERS_V1,
    KafkaTopic.ORDERBOOK_V1,
    KafkaTopic.ANOMALIES_V1,
    KafkaTopic.DLQ_V1,
)


class StreamBrokerPort(Protocol):
    """Streaming broker contract decoupling producers, consumers, and infrastructure."""

    def publish_event(self, topic: str, envelope: EventEnvelopeV1) -> int: ...

    def publish_dlq(self, dlq: DeadLetterEnvelopeV1) -> None: ...

    def consume_for_group(
        self, topic: str, group_id: str, limit: int | None = None
    ) -> list[dict[str, Any]]: ...

    def commit_offset(self, topic: str, group_id: str, processed_offset: int) -> None: ...

    def topic_lag(self, topic: str, group_id: str) -> int: ...
