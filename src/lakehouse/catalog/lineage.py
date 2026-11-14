"""Data Governance Catalog & End-to-End Dataset Lineage Registry (Stage 12)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


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
