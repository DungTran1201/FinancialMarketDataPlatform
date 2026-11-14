"""PySpark Batch Job Specification & Silver Iceberg Deduplication Engine (Bronze -> Silver).

Note: Spark is strictly restricted to scheduled batch/micro-batch Lakehouse processing
and historical backfills (ADR-002). It is never invoked on the per-event real-time path.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


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


class SilverLakehouseMergeEngine:
    """Executes idempotent Bronze -> Silver standardization and `MERGE INTO` deduplication."""

    def __init__(self, lakehouse_root: Path | str = ".local_lakehouse") -> None:
        self._root = Path(lakehouse_root)

    def merge_bronze_klines_to_silver(
        self,
        bronze_parquet_files: list[Path],
    ) -> tuple[Path, list[dict[str, Any]]]:
        """Read Bronze kline Parquet files, deduplicate by natural key, and write Silver table."""
        deduped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
        for pq_file in bronze_parquet_files:
            table = pq.read_table(pq_file)
            for raw_row in table.to_pylist():
                payload = json.loads(str(raw_row["payload_json"]))
                record = {
                    "provider": str(raw_row["provider"]).lower(),
                    "symbol": str(raw_row["symbol"]).upper(),
                    "interval": str(payload.get("interval", "1m")),
                    "open_time": str(payload["open_time"]),
                    "close_time": str(payload["close_time"]),
                    "open_price": float(payload["open_price"]),
                    "high_price": float(payload["high_price"]),
                    "low_price": float(payload["low_price"]),
                    "close_price": float(payload["close_price"]),
                    "base_volume": float(payload["base_volume"]),
                    "quote_volume": float(payload["quote_volume"]),
                    "trade_count": int(payload.get("trade_count", 0)),
                    "is_closed": bool(payload.get("is_closed", True)),
                    "exchange_event_time": str(raw_row["exchange_event_time"]),
                    "ingested_at": str(raw_row["ingested_at"]),
                }
                natural_key = (
                    record["provider"],
                    record["symbol"],
                    record["interval"],
                    record["open_time"],
                )
                existing = deduped.get(natural_key)
                if existing is None or record["exchange_event_time"] >= existing["exchange_event_time"]:
                    deduped[natural_key] = record

        silver_rows = sorted(
            deduped.values(),
            key=lambda r: (r["provider"], r["symbol"], r["interval"], r["open_time"]),
        )
        silver_dir = self._root / "silver" / "market_klines"
        silver_dir.mkdir(parents=True, exist_ok=True)
        out_path = silver_dir / "silver_market_klines.parquet"
        pq.write_table(pa.Table.from_pylist(silver_rows), out_path, compression="ZSTD")
        return out_path, silver_rows
