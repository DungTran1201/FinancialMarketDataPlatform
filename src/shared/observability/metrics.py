"""Shared OpenMetrics / Prometheus Data Observability Collector (Stage 11)."""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

_LATENCY_BUCKETS_MS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0)


class DataObservabilityMetricsCollector:
    """Stage 11 Prometheus Metrics Exporter tracking Data Plane SLIs (`fmdp_*` metrics)."""

    def __init__(self) -> None:
        self.registry = CollectorRegistry()
        self.ingested_events_total = Counter(
            "fmdp_ingested_events_total",
            "Total normalized market events published to Kafka",
            ["provider", "symbol", "event_type"],
            registry=self.registry,
        )
        self.dlq_events_total = Counter(
            "fmdp_dlq_events_total",
            "Total malformed or invariant-violating payloads routed to DLQ",
            ["provider", "error_code"],
            registry=self.registry,
        )
        self.consumer_lag_records = Gauge(
            "fmdp_consumer_lag_records",
            "Uncommitted Kafka consumer group offset lag",
            ["consumer_group", "topic"],
            registry=self.registry,
        )
        self.hot_out_of_order_dropped_total = Counter(
            "fmdp_hot_out_of_order_dropped_total",
            "Total stale events rejected by Redis monotonic timestamp guard (BR-003)",
            ["provider"],
            registry=self.registry,
        )
        self.dq_validation_runs_total = Counter(
            "fmdp_dq_validation_runs_total",
            "Total Great Expectations quality gate runs by outcome",
            ["dataset", "status"],
            registry=self.registry,
        )
        self.gold_mart_rows_gauge = Gauge(
            "fmdp_gold_mart_rows_total",
            "Current materialized row count in Gold analytical marts",
            ["mart_name"],
            registry=self.registry,
        )
        self.stage_processing_duration_ms = Histogram(
            "fmdp_stage_processing_duration_ms",
            "Per-stage processing duration in milliseconds (bounded labels only)",
            ["stage", "mode"],
            buckets=_LATENCY_BUCKETS_MS,
            registry=self.registry,
        )
        self.end_to_end_latency_ms = Histogram(
            "fmdp_end_to_end_latency_ms",
            "Non-summed parallel branch and critical-path E2E latency in milliseconds",
            ["path", "mode"],
            buckets=_LATENCY_BUCKETS_MS,
            registry=self.registry,
        )
        self.stage_events_total = Counter(
            "fmdp_stage_events_total",
            "Total stage executions observed across Data Platform planes",
            ["stage", "status", "mode"],
            registry=self.registry,
        )
        self.serving_requests_total = Counter(
            "fmdp_serving_requests_total",
            "Observability and serving API requests by endpoint and status class",
            ["endpoint", "status"],
            registry=self.registry,
        )

    def record_ingested_event(self, provider: str, symbol: str, event_type: str, count: int = 1) -> None:
        self.ingested_events_total.labels(
            provider=provider.lower(), symbol=symbol.upper(), event_type=event_type
        ).inc(count)

    def record_dlq_event(self, provider: str, error_code: str, count: int = 1) -> None:
        self.dlq_events_total.labels(provider=provider.lower(), error_code=error_code).inc(count)

    def set_consumer_lag(self, consumer_group: str, topic: str, lag: int) -> None:
        self.consumer_lag_records.labels(consumer_group=consumer_group, topic=topic).set(lag)

    def record_dq_run(self, dataset: str, passed: bool) -> None:
        status = "PASSED" if passed else "FAILED"
        self.dq_validation_runs_total.labels(dataset=dataset, status=status).inc()

    def set_gold_mart_rows(self, mart_name: str, row_count: int) -> None:
        self.gold_mart_rows_gauge.labels(mart_name=mart_name).set(row_count)

    def record_stage_duration(
        self, stage: str, duration_ms: float, *, mode: str = "LIVE", status: str = "OK"
    ) -> None:
        """Record bounded-cardinality stage latency histogram and execution counter."""
        bounded_mode = mode if mode in ("LIVE", "LIVE_STARTUP", "DEMO") else "OTHER"
        self.stage_processing_duration_ms.labels(stage=stage, mode=bounded_mode).observe(
            max(0.0, float(duration_ms))
        )
        self.stage_events_total.labels(stage=stage, status=status, mode=bounded_mode).inc()

    def record_e2e_latency(self, path: str, duration_ms: float, *, mode: str = "LIVE") -> None:
        """Record non-summed parallel branch or critical-path E2E latency."""
        bounded_path = path if path in ("hot", "olap", "lakehouse", "critical_serving") else "other"
        bounded_mode = mode if mode in ("LIVE", "LIVE_STARTUP", "DEMO") else "OTHER"
        self.end_to_end_latency_ms.labels(path=bounded_path, mode=bounded_mode).observe(
            max(0.0, float(duration_ms))
        )

    def record_serving_request(self, endpoint: str, status: str) -> None:
        self.serving_requests_total.labels(endpoint=endpoint, status=status).inc()

    def export_prometheus_text(self) -> str:
        """Render standard OpenMetrics / Prometheus exposition text."""
        return generate_latest(self.registry).decode("utf-8")
