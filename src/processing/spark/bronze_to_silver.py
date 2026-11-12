"""PySpark Batch Job Specification: Bronze -> Silver Lakehouse Deduplication & Standardization.

Note: Spark is strictly restricted to scheduled batch/micro-batch Lakehouse processing
and historical backfills (ADR-002). It is never invoked on the per-event real-time path.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SilverMergeJobSpec:
    """Specification for an idempotent Iceberg MERGE INTO job from Bronze to Silver."""

    source_bronze_table: str
    target_silver_table: str
    natural_key_columns: tuple[str, ...]
    version_column: str


SILVER_KLINES_MERGE_SPEC = SilverMergeJobSpec(
    source_bronze_table="lakehouse.bronze.raw_klines",
    target_silver_table="lakehouse.silver.market_klines",
    natural_key_columns=("provider", "symbol", "interval", "open_time"),
    version_column="exchange_event_time",
)

SILVER_TRADES_MERGE_SPEC = SilverMergeJobSpec(
    source_bronze_table="lakehouse.bronze.raw_trades",
    target_silver_table="lakehouse.silver.market_trades",
    natural_key_columns=("provider", "symbol", "trade_id"),
    version_column="ingested_at",
)

