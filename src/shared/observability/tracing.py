"""Unified pipeline trace correlation, parallel-branch latency mathematics, and percentile engine.

Guarantees bounded memory (`deque(maxlen=2000)`), never introduces high-cardinality IDs into
Prometheus label sets (`DATA-RULE-010`), and enforces non-summation across parallel post-Kafka
sink branches (`Redis Hot State` || `ClickHouse OLAP` || `Bronze -> Silver -> Gold`).
"""

from __future__ import annotations

import asyncio
import contextlib
import math
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

CANONICAL_STAGES: tuple[str, ...] = (
    "ingestion",
    "kafka_publish",
    "kafka_consume",
    "redis_hot_write",
    "clickhouse_olap_write",
    "bronze_archive",
    "silver_merge",
    "dq_gate",
    "gold_mart",
    "dlq_route",
    "serving_ready",
)

SERIAL_SPINE_STAGES: tuple[str, ...] = ("ingestion", "kafka_publish", "kafka_consume")
LAKEHOUSE_CHAIN_STAGES: tuple[str, ...] = ("bronze_archive", "silver_merge", "dq_gate", "gold_mart")

WINDOW_SECONDS: dict[str, float | None] = {
    "1m": 60.0,
    "5m": 300.0,
    "15m": 900.0,
    "1h": 3600.0,
    "24h": 86400.0,
    "all": None,
}

BRANCH_LATENCY_FORMULA = (
    "E2E = serial_spine(ingestion + kafka_publish + kafka_consume) + "
    "critical_path(max over completed parallel branches [redis_hot | clickhouse_olap | "
    "bronze->silver->dq->gold]) + serving_ready; parallel branches are NEVER summed."
)


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp string with millisecond precision."""
    return datetime.now(UTC).isoformat()


def parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse an ISO-8601 string into an aware UTC datetime, returning None if invalid."""
    if not value:
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def compute_exchange_to_ingested_lag_ms(
    exchange_event_time: str | None,
    ingested_at: str | None,
) -> float | None:
    """Compute wall-clock ingestion lag (ms) from exchange event timestamp to platform ingestion."""
    ex_dt = parse_iso_datetime(exchange_event_time)
    in_dt = parse_iso_datetime(ingested_at)
    if ex_dt is None or in_dt is None:
        return None
    return round((in_dt - ex_dt).total_seconds() * 1000.0, 3)


def compute_parallel_branch_latencies(
    stage_durations_ms: dict[str, float],
    final_status: str = "SERVING_COMPLETE",
) -> dict[str, float | None]:
    """Compute per-branch and non-summed critical-path E2E serving latencies in milliseconds."""
    serial_spine = sum(
        float(stage_durations_ms[s]) for s in SERIAL_SPINE_STAGES if s in stage_durations_ms
    )
    hot_branch = (
        round(float(stage_durations_ms["redis_hot_write"]), 3)
        if "redis_hot_write" in stage_durations_ms
        else None
    )
    olap_branch = (
        round(float(stage_durations_ms["clickhouse_olap_write"]), 3)
        if "clickhouse_olap_write" in stage_durations_ms
        else None
    )
    lh_parts = [float(stage_durations_ms[s]) for s in LAKEHOUSE_CHAIN_STAGES if s in stage_durations_ms]
    lakehouse_branch = round(sum(lh_parts), 3) if lh_parts else None
    serving_ready = float(stage_durations_ms.get("serving_ready", 0.0))

    active_parallel = [b for b in (hot_branch, olap_branch, lakehouse_branch) if b is not None]
    if active_parallel:
        critical_branch = max(active_parallel)
    elif "dlq_route" in stage_durations_ms:
        critical_branch = float(stage_durations_ms["dlq_route"])
    else:
        critical_branch = 0.0

    serving_hot_e2e = (
        round(serial_spine + hot_branch + serving_ready, 3) if hot_branch is not None else None
    )
    serving_olap_e2e = (
        round(serial_spine + olap_branch + serving_ready, 3) if olap_branch is not None else None
    )
    serving_lakehouse_e2e = (
        round(serial_spine + lakehouse_branch + serving_ready, 3)
        if lakehouse_branch is not None
        else None
    )

    is_terminal_or_serving = final_status in (
        "SERVING_HOT",
        "SERVING_COMPLETE",
        "DLQ_FAILED",
        "DQ_BLOCKED",
    ) or bool(active_parallel)
    e2e_serving = (
        round(serial_spine + critical_branch + serving_ready, 3) if is_terminal_or_serving else None
    )

    return {
        "serial_spine_ms": round(serial_spine, 3),
        "hot_branch_ms": hot_branch,
        "olap_branch_ms": olap_branch,
        "lakehouse_branch_ms": lakehouse_branch,
        "serving_hot_e2e_ms": serving_hot_e2e,
        "serving_olap_e2e_ms": serving_olap_e2e,
        "serving_lakehouse_e2e_ms": serving_lakehouse_e2e,
        "end_to_end_serving_ms": e2e_serving,
    }


def compute_percentiles(values: list[float]) -> dict[str, Any]:
    """Return min/avg/P50/P95/P99/max summary statistics using linear interpolation."""
    if not values:
        return {
            "count": 0,
            "min": None,
            "avg": None,
            "p50": None,
            "p95": None,
            "p99": None,
            "max": None,
        }
    ordered = sorted(float(v) for v in values)
    n = len(ordered)

    def _pct(q: float) -> float:
        if n == 1:
            return round(ordered[0], 3)
        pos = q * (n - 1)
        lo = int(math.floor(pos))
        hi = min(lo + 1, n - 1)
        frac = pos - lo
        val = ordered[lo] * (1.0 - frac) + ordered[hi] * frac
        return round(val, 3)

    return {
        "count": n,
        "min": round(ordered[0], 3),
        "avg": round(sum(ordered) / n, 3),
        "p50": _pct(0.50),
        "p95": _pct(0.95),
        "p99": _pct(0.99),
        "max": round(ordered[-1], 3),
    }


@dataclass(slots=True)
class EventLifecycleTrace:
    """Unified 10-timestamp trace of a single platform event across all parallel branches."""

    event_id: str
    correlation_id: str
    execution_mode: str = "LIVE"  # LIVE | LIVE_STARTUP | DEMO
    provider: str = "binance"
    symbol: str = "BTCUSDT"
    event_type: str = "trade"
    topic: str | None = None
    partition: int | None = None
    offset: int | None = None
    consumer_groups_acked: list[str] = field(default_factory=list)
    exchange_event_time: str | None = None
    ingested_at: str | None = None
    kafka_published_at: str | None = None
    kafka_consumed_at: str | None = None
    redis_written_at: str | None = None
    clickhouse_written_at: str | None = None
    bronze_committed_at: str | None = None
    silver_processed_at: str | None = None
    gold_loaded_at: str | None = None
    serving_available_at: str | None = None
    stage_durations_ms: dict[str, float] = field(default_factory=dict)
    final_status: str = "IN_FLIGHT"  # IN_FLIGHT | SERVING_HOT | SERVING_COMPLETE | DLQ_FAILED | DQ_BLOCKED
    error_detail: str | None = None
    recorded_epoch_s: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Serialize trace with computed parallel-branch latencies and source lag."""
        branches = compute_parallel_branch_latencies(
            self.stage_durations_ms, final_status=self.final_status
        )
        ex_lag = compute_exchange_to_ingested_lag_ms(self.exchange_event_time, self.ingested_at)
        payload = asdict(self)
        payload["exchange_to_ingested_lag_ms"] = ex_lag
        payload["timestamps"] = {
            "exchange_event_time": self.exchange_event_time,
            "ingested_at": self.ingested_at,
            "kafka_published_at": self.kafka_published_at,
            "kafka_consumed_at": self.kafka_consumed_at,
            "redis_written_at": self.redis_written_at,
            "clickhouse_written_at": self.clickhouse_written_at,
            "bronze_committed_at": self.bronze_committed_at,
            "silver_processed_at": self.silver_processed_at,
            "gold_loaded_at": self.gold_loaded_at,
            "serving_available_at": self.serving_available_at,
        }
        payload["branch_latencies_ms"] = branches
        payload["hot_branch_ms"] = branches["hot_branch_ms"]
        payload["olap_branch_ms"] = branches["olap_branch_ms"]
        payload["lakehouse_branch_ms"] = branches["lakehouse_branch_ms"]
        payload["end_to_end_serving_ms"] = branches["end_to_end_serving_ms"]
        payload["serving_hot_e2e_ms"] = branches["serving_hot_e2e_ms"]
        payload["serving_olap_e2e_ms"] = branches["serving_olap_e2e_ms"]
        payload["serving_lakehouse_e2e_ms"] = branches["serving_lakehouse_e2e_ms"]
        return payload


class PipelineTraceRegistry:
    """Thread-safe bounded registry of `EventLifecycleTrace` records and SSE broadcast queues."""

    def __init__(self, max_traces: int = 2000) -> None:
        self._lock = threading.RLock()
        self._max_traces = max_traces
        self._traces_order: deque[str] = deque()
        self._traces_by_id: dict[str, EventLifecycleTrace] = {}
        self._subscribers: dict[int, tuple[asyncio.AbstractEventLoop, asyncio.Queue[dict[str, Any]]]] = {}
        self._next_sub_id = 1
        self._cumulative_ingested = 0
        self._cumulative_processed = 0
        self._cumulative_failed = 0
        self._cumulative_dq_blocked = 0
        self._stage_callbacks: list[Callable[[EventLifecycleTrace], None]] = []

    def register_listener(self, cb: Callable[[EventLifecycleTrace], None]) -> None:
        with self._lock:
            self._stage_callbacks.append(cb)

    def _evict_if_needed(self) -> None:
        while len(self._traces_order) > self._max_traces:
            oldest_id = self._traces_order.popleft()
            self._traces_by_id.pop(oldest_id, None)

    def upsert_trace(self, trace: EventLifecycleTrace) -> EventLifecycleTrace:
        """Insert or update a trace record and notify active SSE/WS subscribers."""
        with self._lock:
            is_new = trace.event_id not in self._traces_by_id
            prev_status = self._traces_by_id[trace.event_id].final_status if not is_new else None
            self._traces_by_id[trace.event_id] = trace
            if is_new:
                self._traces_order.append(trace.event_id)
                self._cumulative_ingested += 1
                self._evict_if_needed()

            if trace.final_status in ("SERVING_HOT", "SERVING_COMPLETE") and prev_status not in (
                "SERVING_HOT",
                "SERVING_COMPLETE",
            ):
                self._cumulative_processed += 1
            elif trace.final_status == "DLQ_FAILED" and prev_status != "DLQ_FAILED":
                self._cumulative_failed += 1
            elif trace.final_status == "DQ_BLOCKED" and prev_status != "DQ_BLOCKED":
                self._cumulative_dq_blocked += 1

            snapshot = trace.to_dict()
            subscribers = list(self._subscribers.items())
            callbacks = list(self._stage_callbacks)

        for cb in callbacks:
            with contextlib.suppress(Exception):
                cb(trace)

        for _sub_id, (loop, queue) in subscribers:
            if loop.is_closed():
                continue
            with contextlib.suppress(RuntimeError):
                loop.call_soon_threadsafe(self._enqueue_nonblocking, queue, snapshot)
        return trace

    @staticmethod
    def _enqueue_nonblocking(queue: asyncio.Queue[dict[str, Any]], payload: dict[str, Any]) -> None:
        if queue.full():
            with contextlib.suppress(asyncio.QueueEmpty):
                queue.get_nowait()
        with contextlib.suppress(asyncio.QueueFull):
            queue.put_nowait(payload)

    def update_stage(
        self,
        event_id: str,
        *,
        stage: str,
        duration_ms: float,
        timestamp_field: str | None = None,
        timestamp_value: str | None = None,
        consumer_group: str | None = None,
        final_status: str | None = None,
        error_detail: str | None = None,
        topic: str | None = None,
        partition: int | None = None,
        offset: int | None = None,
    ) -> EventLifecycleTrace | None:
        """Append stage timing, timestamp, and consumer group state to an existing trace."""
        with self._lock:
            existing = self._traces_by_id.get(event_id)
            if existing is None:
                return None
            existing.stage_durations_ms[stage] = round(max(0.0, float(duration_ms)), 3)
            if timestamp_field and hasattr(existing, timestamp_field):
                setattr(existing, timestamp_field, timestamp_value or utc_now_iso())
            if consumer_group and consumer_group not in existing.consumer_groups_acked:
                existing.consumer_groups_acked.append(consumer_group)
            if topic is not None:
                existing.topic = topic
            if partition is not None:
                existing.partition = partition
            if offset is not None:
                existing.offset = offset
            if final_status is not None:
                existing.final_status = final_status
            if error_detail is not None:
                existing.error_detail = error_detail
            existing.recorded_epoch_s = time.time()
            return self.upsert_trace(existing)

    def subscribe(self, loop: asyncio.AbstractEventLoop) -> tuple[int, asyncio.Queue[dict[str, Any]]]:
        """Register an async queue for live trace notifications."""
        with self._lock:
            sub_id = self._next_sub_id
            self._next_sub_id += 1
            queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=256)
            self._subscribers[sub_id] = (loop, queue)
            return sub_id, queue

    def unsubscribe(self, sub_id: int) -> None:
        """Remove an SSE/WS subscriber cleanly."""
        with self._lock:
            self._subscribers.pop(sub_id, None)

    def get_trace(self, event_id: str) -> dict[str, Any] | None:
        with self._lock:
            trace = self._traces_by_id.get(event_id)
            return trace.to_dict() if trace is not None else None

    def _filter_traces(
        self,
        *,
        window: str = "all",
        mode: str | None = None,
        provider: str | None = None,
        symbol: str | None = None,
        status: str | None = None,
        topic: str | None = None,
        slow_threshold_ms: float | None = None,
        only_errors: bool = False,
    ) -> list[EventLifecycleTrace]:
        now = time.time()
        window_sec = WINDOW_SECONDS.get(window, None)
        cutoff = (now - window_sec) if window_sec is not None else None

        with self._lock:
            items = [self._traces_by_id[eid] for eid in reversed(self._traces_order) if eid in self._traces_by_id]

        filtered: list[EventLifecycleTrace] = []
        for t in items:
            if cutoff is not None and t.recorded_epoch_s < cutoff:
                continue
            if mode and mode != "ALL" and t.execution_mode != mode:
                continue
            if provider and provider != "ALL" and t.provider != provider:
                continue
            if symbol and symbol != "ALL" and t.symbol != symbol:
                continue
            if status and status != "ALL" and t.final_status != status:
                continue
            if topic and topic != "ALL" and t.topic != topic:
                continue
            if only_errors and t.final_status not in ("DLQ_FAILED", "DQ_BLOCKED") and not t.error_detail:
                continue
            if slow_threshold_ms is not None:
                branches = compute_parallel_branch_latencies(t.stage_durations_ms, t.final_status)
                e2e = branches["end_to_end_serving_ms"] or 0.0
                if e2e < slow_threshold_ms:
                    continue
            filtered.append(t)
        return filtered

    def query_traces(
        self,
        *,
        window: str = "all",
        mode: str | None = None,
        provider: str | None = None,
        symbol: str | None = None,
        status: str | None = None,
        topic: str | None = None,
        slow_threshold_ms: float | None = None,
        only_errors: bool = False,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        matched = self._filter_traces(
            window=window,
            mode=mode,
            provider=provider,
            symbol=symbol,
            status=status,
            topic=topic,
            slow_threshold_ms=slow_threshold_ms,
            only_errors=only_errors,
        )
        return [t.to_dict() for t in matched[: max(1, min(limit, 500))]]

    def get_summary_counts(
        self,
        *,
        window: str = "all",
        mode: str | None = None,
        provider: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        traces = self._filter_traces(window=window, mode=mode, provider=provider, symbol=symbol)
        window_sec = WINDOW_SECONDS.get(window, None)
        if traces:
            span = (
                window_sec
                if window_sec is not None
                else max(1.0, time.time() - min(t.recorded_epoch_s for t in traces))
            )
        else:
            span = window_sec or 1.0

        processed = sum(1 for t in traces if t.final_status in ("SERVING_HOT", "SERVING_COMPLETE"))
        failed = sum(1 for t in traces if t.final_status == "DLQ_FAILED")
        dq_blocked = sum(1 for t in traces if t.final_status == "DQ_BLOCKED")
        in_flight = sum(1 for t in traces if t.final_status == "IN_FLIGHT")
        live_count = sum(1 for t in traces if t.execution_mode in ("LIVE", "LIVE_STARTUP"))
        demo_count = sum(1 for t in traces if t.execution_mode == "DEMO")

        with self._lock:
            cumulative = {
                "ingested": self._cumulative_ingested,
                "processed": self._cumulative_processed,
                "failed_dlq": self._cumulative_failed,
                "dq_blocked": self._cumulative_dq_blocked,
                "retained_in_memory": len(self._traces_by_id),
                "max_traces": self._max_traces,
            }

        return {
            "window": window,
            "window_seconds": span,
            "events_ingested": len(traces),
            "events_processed": processed,
            "events_failed_dlq": failed,
            "events_dq_blocked": dq_blocked,
            "events_in_flight": in_flight,
            "live_events": live_count,
            "demo_events": demo_count,
            "throughput_events_per_sec": round(len(traces) / max(1.0, span), 3),
            "cumulative": cumulative,
        }

    def compute_latency_analytics(
        self,
        *,
        window: str = "all",
        mode: str | None = None,
        provider: str | None = None,
        symbol: str | None = None,
        slow_threshold_ms: float = 25.0,
        bucket_count: int = 20,
    ) -> dict[str, Any]:
        """Compute stage percentiles, parallel branch percentiles, histogram, and clickable time buckets."""
        traces = self._filter_traces(window=window, mode=mode, provider=provider, symbol=symbol)
        # Oldest-first ordering for time buckets
        chronological = list(reversed(traces))

        stage_samples: dict[str, list[float]] = {stage: [] for stage in CANONICAL_STAGES}
        branch_samples: dict[str, list[float]] = {
            "serial_spine_ms": [],
            "hot_branch_ms": [],
            "olap_branch_ms": [],
            "lakehouse_branch_ms": [],
            "serving_hot_e2e_ms": [],
            "serving_olap_e2e_ms": [],
            "serving_lakehouse_e2e_ms": [],
            "end_to_end_serving_ms": [],
        }
        e2e_pairs: list[tuple[EventLifecycleTrace, float]] = []
        slow_or_failed: list[dict[str, Any]] = []

        for t in chronological:
            for stage_name, val in t.stage_durations_ms.items():
                if stage_name in stage_samples:
                    stage_samples[stage_name].append(float(val))
            branches = compute_parallel_branch_latencies(t.stage_durations_ms, t.final_status)
            for key, samples in branch_samples.items():
                bval = branches.get(key)
                if bval is not None:
                    samples.append(float(bval))

            e2e = branches["end_to_end_serving_ms"]
            if e2e is not None:
                e2e_pairs.append((t, float(e2e)))
            if (e2e is not None and e2e >= slow_threshold_ms) or t.final_status in (
                "DLQ_FAILED",
                "DQ_BLOCKED",
            ):
                slow_or_failed.append(t.to_dict())

        stage_stats = {stage: compute_percentiles(vals) for stage, vals in stage_samples.items()}
        branch_stats = {name: compute_percentiles(vals) for name, vals in branch_samples.items()}

        # Distribution histogram for end_to_end_serving_ms
        hist_bins = [
            ("0-1ms", 0.0, 1.0),
            ("1-5ms", 1.0, 5.0),
            ("5-15ms", 5.0, 15.0),
            ("15-50ms", 15.0, 50.0),
            ("50-150ms", 50.0, 150.0),
            ("150ms+", 150.0, float("inf")),
        ]
        histogram = []
        all_e2e = [e for _t, e in e2e_pairs]
        for label, lo, hi in hist_bins:
            matching_ids = [t.event_id for t, e in e2e_pairs if lo <= e < hi]
            histogram.append({"bucket": label, "count": len(matching_ids), "event_ids": matching_ids[:50]})

        # Clickable time buckets
        buckets: list[dict[str, Any]] = []
        if chronological:
            t_min = chronological[0].recorded_epoch_s
            t_max = max(chronological[-1].recorded_epoch_s, t_min + 1.0)
            width = max(0.05, (t_max - t_min) / max(1, bucket_count))
            for idx in range(bucket_count):
                b_start = t_min + idx * width
                b_end = t_min + (idx + 1) * width + (1e-6 if idx == bucket_count - 1 else 0.0)
                bucket_traces = [t for t in chronological if b_start <= t.recorded_epoch_s < b_end]
                if not bucket_traces:
                    continue
                bucket_e2e = [
                    compute_parallel_branch_latencies(t.stage_durations_ms, t.final_status)[
                        "end_to_end_serving_ms"
                    ]
                    for t in bucket_traces
                ]
                valid_e2e = [float(v) for v in bucket_e2e if v is not None]
                stats = compute_percentiles(valid_e2e)
                buckets.append(
                    {
                        "bucket_index": idx,
                        "start_iso": datetime.fromtimestamp(b_start, tz=UTC).isoformat(),
                        "end_iso": datetime.fromtimestamp(b_end, tz=UTC).isoformat(),
                        "label": datetime.fromtimestamp(b_end, tz=UTC).strftime("%H:%M:%S"),
                        "count": len(bucket_traces),
                        "error_count": sum(
                            1 for t in bucket_traces if t.final_status in ("DLQ_FAILED", "DQ_BLOCKED")
                        ),
                        "avg_ms": stats["avg"] or 0.0,
                        "p50_ms": stats["p50"] or 0.0,
                        "p95_ms": stats["p95"] or 0.0,
                        "max_ms": stats["max"] or 0.0,
                        "event_ids": [t.event_id for t in bucket_traces[:50]],
                    }
                )

        return {
            "window": window,
            "formula": BRANCH_LATENCY_FORMULA,
            "trace_count": len(traces),
            "stage_stats": stage_stats,
            "branch_stats": branch_stats,
            "overall_e2e": compute_percentiles(all_e2e),
            "histogram": histogram,
            "timeseries_buckets": buckets,
            "slow_or_failed_traces": list(reversed(slow_or_failed))[:50],
        }

