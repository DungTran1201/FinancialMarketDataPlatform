"""Shared OpenMetrics / Prometheus Data Observability Collector (Stage 11)."""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, generate_latest


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

    def export_prometheus_text(self) -> str:
        """Render standard OpenMetrics / Prometheus exposition text."""
        return generate_latest(self.registry).decode("utf-8")
