"""Statistical Anomaly Detector with 15-Minute Cooldown Deduplication (Plane A -> Plane C Trigger)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime

from src.shared.contracts.events import (
    SCHEMA_VERSION_V1,
    EventEnvelopeV1,
    EventType,
    compute_deterministic_event_id,
)


@dataclass(frozen=True, slots=True)
class DetectedMarketAnomaly:
    """Deterministic statistical anomaly observation."""

    provider: str
    symbol: str
    detector_name: str
    z_score: float
    threshold: float
    latest_value: float
    mean_value: float
    std_dev: float
    detected_at: datetime


class StatisticalAnomalyDetector:
    """Computes rolling return/volume Z-scores and suppresses duplicate alerts via 15m cooldown (`ADR-006`)."""

    CONSUMER_GROUP = "cg.anomaly.detector.v1"

    def __init__(self, zscore_threshold: float = 2.5, cooldown_seconds: int = 900) -> None:
        self._threshold = zscore_threshold
        self._cooldown_seconds = cooldown_seconds
        self._cooldown_registry: dict[str, float] = {}
        self._suppressed_count: int = 0

    @staticmethod
    def build_cooldown_key(provider: str, symbol: str, detector_name: str) -> str:
        return f"agent:cooldown:{provider.lower()}:{symbol.upper()}:{detector_name}"

    def evaluate_series(
        self,
        provider: str,
        symbol: str,
        values: list[float],
        detector_name: str = "return_zscore",
        now_utc: datetime | None = None,
    ) -> tuple[EventEnvelopeV1 | None, DetectedMarketAnomaly | None]:
        """Evaluate a numeric series for a Z-score breach and emit an anomaly event if not in cooldown."""
        if len(values) < 5:
            return None, None

        now = now_utc or datetime.now(UTC)
        baseline = values[:-1]
        latest = values[-1]
        mean_val = sum(baseline) / len(baseline)
        variance = sum((x - mean_val) ** 2 for x in baseline) / max(1, len(baseline) - 1)
        std_dev = math.sqrt(variance)
        if std_dev <= 1e-12:
            return None, None

        z_score = (latest - mean_val) / std_dev
        if abs(z_score) < self._threshold:
            return None, None

        cooldown_key = self.build_cooldown_key(provider, symbol, detector_name)
        now_ts = now.timestamp()
        expires_at = self._cooldown_registry.get(cooldown_key, 0.0)
        if now_ts < expires_at:
            self._suppressed_count += 1
            return None, None

        self._cooldown_registry[cooldown_key] = now_ts + self._cooldown_seconds
        anomaly = DetectedMarketAnomaly(
            provider=provider.lower(),
            symbol=symbol.upper(),
            detector_name=detector_name,
            z_score=round(z_score, 4),
            threshold=self._threshold,
            latest_value=latest,
            mean_value=round(mean_val, 6),
            std_dev=round(std_dev, 6),
            detected_at=now,
        )
        event_id = compute_deterministic_event_id(
            provider,
            EventType.ANOMALY,
            symbol,
            f"{detector_name}:{int(now_ts)}",
        )
        envelope = EventEnvelopeV1(
            event_id=event_id,
            schema_version=SCHEMA_VERSION_V1,
            provider=provider.lower(),
            symbol=symbol.upper(),
            event_type=EventType.ANOMALY,
            exchange_event_time=now,
            ingested_at=now,
            payload={
                "detector_name": anomaly.detector_name,
                "z_score": anomaly.z_score,
                "threshold": anomaly.threshold,
                "latest_value": anomaly.latest_value,
                "mean_value": anomaly.mean_value,
                "std_dev": anomaly.std_dev,
                "severity": "CRITICAL" if abs(z_score) >= 3.5 else "HIGH",
            },
        )
        return envelope, anomaly

    @property
    def suppressed_alerts_count(self) -> int:
        return self._suppressed_count
