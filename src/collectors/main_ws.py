"""Real-time WebSocket Ingestion Collector Service Entrypoint (Plane A: `collector-ws`)."""

from __future__ import annotations

import logging
import random
from datetime import UTC, datetime
from typing import Any

from src.collectors.normalizer import BinancePayloadNormalizer
from src.collectors.publisher import (
    DetectedStreamGap,
    PartitionedEventStreamingBroker,
    SequenceAndGapDetector,
)
from src.shared.config import PlatformConfig
from src.shared.contracts.events import EventEnvelopeV1, EventType

logger = logging.getLogger(__name__)


def compute_reconnect_backoff_seconds(attempt: int, deterministic_jitter: float | None = None) -> float:
    """Compute bounded exponential backoff with full jitter: `min(60, 1 * 2^attempt) + uniform(0, 1.0)`."""
    base = float(min(60, 1 * (2 ** max(0, attempt))))
    jitter = deterministic_jitter if deterministic_jitter is not None else random.uniform(0.0, 1.0)
    return round(base + jitter, 4)


class WebSocketStreamCollector:
    """Real-time WebSocket stream collector with sequence gap detection and DLQ routing."""

    def __init__(
        self,
        broker: PartitionedEventStreamingBroker,
        normalizer: BinancePayloadNormalizer | None = None,
        gap_detector: SequenceAndGapDetector | None = None,
    ) -> None:
        self.broker = broker
        self.normalizer = normalizer or BinancePayloadNormalizer()
        self.gap_detector = gap_detector or SequenceAndGapDetector()
        self._ingested_count = 0
        self._dlq_count = 0
        self._reconnect_attempts = 0

    async def process_ws_frame(
        self,
        raw_frame: dict[str, Any],
        source_topic: str = "market.raw.ws.v1",
        ingested_at: datetime | None = None,
    ) -> tuple[EventEnvelopeV1 | None, DetectedStreamGap | None]:
        """Normalize incoming WS frame, detect kline sequence gaps, and publish to Kafka or DLQ."""
        env, dlq = self.normalizer.normalize_or_route_dlq(
            raw_frame,
            source_topic=source_topic,
            ingested_at=ingested_at or datetime.now(UTC),
        )
        if dlq is not None:
            await self.broker.publish_dlq(dlq)
            self._dlq_count += 1
            return None, None

        assert env is not None
        gap: DetectedStreamGap | None = None
        if env.event_type == EventType.KLINE:
            open_dt = datetime.fromisoformat(str(env.payload["open_time"]))
            interval = str(env.payload.get("interval", "1m"))
            gap = self.gap_detector.observe_kline(env.provider, env.symbol, interval, open_dt)

        topic = self.broker.resolve_topic_for_event(env)
        await self.broker.publish_event(topic, env)
        self._ingested_count += 1
        return env, gap

    def record_reconnect_attempt(self, deterministic_jitter: float = 0.25) -> float:
        """Increment reconnect counter and return computed backoff delay in seconds."""
        delay = compute_reconnect_backoff_seconds(
            self._reconnect_attempts, deterministic_jitter=deterministic_jitter
        )
        self._reconnect_attempts += 1
        return delay

    @property
    def stats(self) -> dict[str, int]:
        return {
            "ingested_count": self._ingested_count,
            "dlq_count": self._dlq_count,
            "reconnect_attempts": self._reconnect_attempts,
            "detected_gaps": len(self.gap_detector.detected_gaps),
        }


def main() -> None:
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info(
        "Initialized collector-ws service for provider=%s targeting Kafka=%s",
        config.default_provider,
        config.kafka_bootstrap_servers,
    )


if __name__ == "__main__":
    main()
