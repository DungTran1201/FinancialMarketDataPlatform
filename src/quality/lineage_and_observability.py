"""Stage 11 (Prometheus Data Observability) & Stage 12 (Data Governance, Lineage & Retention Registry)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from prometheus_client import CollectorRegistry, Counter, Gauge, generate_latest


@dataclass(frozen=True, slots=True)
class DatasetGovernanceNode:
    """Registered dataset node in the Data Platform Governance & Retention Catalog (Stage 12)."""

    dataset_id: str
    layer: str  # SOURCE | STREAM | HOT | OLAP | BRONZE | SILVER | GOLD | SERVING
    owner_role: str
    retention_policy: str
    freshness_slo_seconds: int
    natural_key: tuple[str, ...]
    schema_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class LineageEdge:
    """Directed lineage edge connecting upstream dataset to downstream dataset via a transformation job."""

    upstream_dataset: str
    downstream_dataset: str
    transformation_job: str
    stage_number: int
    last_executed_at: str
    records_processed: int


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


class DataLineageGovernanceRegistry:
    """Stage 12 Data Governance Catalog tracking dataset ownership, retention SLAs, and lineage graph."""

    def __init__(self) -> None:
        self._nodes: dict[str, DatasetGovernanceNode] = {}
        self._edges: list[LineageEdge] = []
        self._register_canonical_datasets()

    def _register_canonical_datasets(self) -> None:
        canonical = [
            DatasetGovernanceNode(
                dataset_id="exchange.binance.spot_api",
                layer="SOURCE",
                owner_role="data-engineer",
                retention_policy="live_stream_and_rest_archive",
                freshness_slo_seconds=1,
                natural_key=("symbol", "event_time"),
            ),
            DatasetGovernanceNode(
                dataset_id="kafka.market.raw.klines.v1",
                layer="STREAM",
                owner_role="data-platform-architect",
                retention_policy="7d_or_20GB_per_topic",
                freshness_slo_seconds=1,
                natural_key=("provider", "symbol", "open_time"),
            ),
            DatasetGovernanceNode(
                dataset_id="kafka.market.raw.trades.v1",
                layer="STREAM",
                owner_role="data-platform-architect",
                retention_policy="7d_or_20GB_per_topic",
                freshness_slo_seconds=1,
                natural_key=("provider", "symbol", "trade_id"),
            ),
            DatasetGovernanceNode(
                dataset_id="redis.market.hot_state.v1",
                layer="HOT",
                owner_role="data-engineer",
                retention_policy="ttl_120s_to_300s_volatile_lru",
                freshness_slo_seconds=2,
                natural_key=("provider", "symbol"),
            ),
            DatasetGovernanceNode(
                dataset_id="clickhouse.market_data.klines_1m",
                layer="OLAP",
                owner_role="analytics-engineer",
                retention_policy="90d_hot_nvme_then_s3_cold",
                freshness_slo_seconds=5,
                natural_key=("provider", "symbol", "interval", "open_time"),
            ),
            DatasetGovernanceNode(
                dataset_id="lakehouse.bronze.raw_events",
                layer="BRONZE",
                owner_role="data-engineer",
                retention_policy="365d_immutable_zstd_parquet",
                freshness_slo_seconds=300,
                natural_key=("event_id",),
            ),
            DatasetGovernanceNode(
                dataset_id="lakehouse.silver.market_klines",
                layer="SILVER",
                owner_role="data-engineer",
                retention_policy="730d_iceberg_v2_compacted",
                freshness_slo_seconds=900,
                natural_key=("provider", "symbol", "interval", "open_time"),
            ),
            DatasetGovernanceNode(
                dataset_id="lakehouse.silver.market_trades",
                layer="SILVER",
                owner_role="data-engineer",
                retention_policy="730d_iceberg_v2_compacted",
                freshness_slo_seconds=900,
                natural_key=("provider", "symbol", "trade_id"),
            ),
            DatasetGovernanceNode(
                dataset_id="lakehouse.gold.fct_daily_market_summary",
                layer="GOLD",
                owner_role="analytics-engineer",
                retention_policy="indefinite_curated_mart",
                freshness_slo_seconds=3600,
                natural_key=("provider", "symbol", "trading_date"),
            ),
            DatasetGovernanceNode(
                dataset_id="lakehouse.gold.fct_realized_volatility",
                layer="GOLD",
                owner_role="analytics-engineer",
                retention_policy="indefinite_curated_mart",
                freshness_slo_seconds=3600,
                natural_key=("provider", "symbol", "interval"),
            ),
            DatasetGovernanceNode(
                dataset_id="lakehouse.gold.fct_orderbook_liquidity",
                layer="GOLD",
                owner_role="analytics-engineer",
                retention_policy="indefinite_curated_mart",
                freshness_slo_seconds=3600,
                natural_key=("provider", "symbol", "exchange_event_time"),
            ),
            DatasetGovernanceNode(
                dataset_id="serving.application_and_intelligence_planes",
                layer="SERVING",
                owner_role="system-architect",
                retention_policy="stateless_api_and_tool_gateway",
                freshness_slo_seconds=2,
                natural_key=("endpoint", "symbol"),
            ),
        ]
        for node in canonical:
            self._nodes[node.dataset_id] = node

    def record_lineage_edge(
        self,
        upstream_dataset: str,
        downstream_dataset: str,
        transformation_job: str,
        stage_number: int,
        records_processed: int,
    ) -> LineageEdge:
        edge = LineageEdge(
            upstream_dataset=upstream_dataset,
            downstream_dataset=downstream_dataset,
            transformation_job=transformation_job,
            stage_number=stage_number,
            last_executed_at=datetime.now(UTC).isoformat(),
            records_processed=records_processed,
        )
        # Replace existing edge for same (upstream, downstream, job) to keep graph clean
        self._edges = [
            e
            for e in self._edges
            if not (
                e.upstream_dataset == upstream_dataset
                and e.downstream_dataset == downstream_dataset
                and e.transformation_job == transformation_job
            )
        ]
        self._edges.append(edge)
        return edge

    def export_lineage_catalog(self) -> dict[str, Any]:
        return {
            "total_datasets": len(self._nodes),
            "total_lineage_edges": len(self._edges),
            "datasets": [
                {
                    "dataset_id": n.dataset_id,
                    "layer": n.layer,
                    "owner_role": n.owner_role,
                    "retention_policy": n.retention_policy,
                    "freshness_slo_seconds": n.freshness_slo_seconds,
                    "natural_key": list(n.natural_key),
                    "schema_version": n.schema_version,
                }
                for n in self._nodes.values()
            ],
            "lineage_edges": [
                {
                    "upstream_dataset": e.upstream_dataset,
                    "downstream_dataset": e.downstream_dataset,
                    "transformation_job": e.transformation_job,
                    "stage_number": e.stage_number,
                    "last_executed_at": e.last_executed_at,
                    "records_processed": e.records_processed,
                }
                for e in sorted(self._edges, key=lambda x: (x.stage_number, x.upstream_dataset))
            ],
        }

