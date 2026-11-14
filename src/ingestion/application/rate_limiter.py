"""Ingestion application token-bucket weight governor & sequence gap detector."""

from __future__ import annotations

import time
from datetime import datetime, timedelta

from src.ingestion.domain.models import DetectedStreamGap


class TokenBucketRateLimiter:
    """Enforces provider HTTP weight budgets (`X-MBX-USED-WEIGHT-1M` <= 80% of 1,200/min ceiling)."""

    def __init__(self, max_weight_per_minute: int = 1200, safety_ratio: float = 0.80) -> None:
        self.max_weight_per_minute = max_weight_per_minute
        self.safe_weight_ceiling = int(max_weight_per_minute * safety_ratio)
        self._used_weight: int = 0
        self._window_started_at: float = time.monotonic()
        self._throttle_events: int = 0

    def record_request_weight(self, weight: int = 2, reported_header_weight: int | None = None) -> float:
        """Consume request weight and return required backoff delay in seconds (0.0 if within budget)."""
        now = time.monotonic()
        if now - self._window_started_at >= 60.0:
            self._used_weight = 0
            self._window_started_at = now

        if reported_header_weight is not None:
            self._used_weight = max(self._used_weight, reported_header_weight)
        else:
            self._used_weight += weight

        if self._used_weight >= self.safe_weight_ceiling:
            self._throttle_events += 1
            return max(0.001, 60.0 - (now - self._window_started_at))
        return 0.0

    @property
    def used_weight(self) -> int:
        return self._used_weight

    @property
    def throttle_events(self) -> int:
        return self._throttle_events


class SequenceAndGapDetector:
    """Detects sequence/timestamp gaps in real-time streams and emits deterministic backfill ranges."""

    def __init__(self) -> None:
        self._last_kline_open_time: dict[tuple[str, str, str], datetime] = {}
        self._detected_gaps: list[DetectedStreamGap] = []

    def observe_kline(
        self,
        provider: str,
        symbol: str,
        interval: str,
        open_time: datetime,
    ) -> DetectedStreamGap | None:
        """Track kline `open_time` and return a `DetectedStreamGap` if candles were skipped."""
        step = timedelta(minutes=1 if interval == "1m" else 5 if interval == "5m" else 60)
        key = (provider.lower(), symbol.upper(), interval)
        prev = self._last_kline_open_time.get(key)
        self._last_kline_open_time[key] = max(open_time, prev) if prev else open_time

        if prev is not None and open_time > prev + step:
            missing = int((open_time - prev) // step) - 1
            gap = DetectedStreamGap(
                provider=provider.lower(),
                symbol=symbol.upper(),
                interval=interval,
                gap_start=prev + step,
                gap_end=open_time,
                missing_candles=missing,
            )
            self._detected_gaps.append(gap)
            return gap
        return None

    @property
    def detected_gaps(self) -> tuple[DetectedStreamGap, ...]:
        return tuple(self._detected_gaps)
