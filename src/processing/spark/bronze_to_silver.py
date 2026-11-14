"""PySpark Batch Job Specification, Silver Iceberg Deduplication & Compaction Engine (Bronze -> Silver).

Note: Spark is strictly restricted to scheduled batch/micro-batch Lakehouse processing
and historical backfills (ADR-002). It is never invoked on the per-event real-time path.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
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

SILVER_ORDERBOOK_MERGE_SPEC = SilverMergeJobSpec(
    source_bronze_table="lakehouse.bronze.raw_orderbook",
    target_silver_table="lakehouse.silver.orderbook_snapshots",
    natural_key_columns=("provider", "symbol", "exchange_event_time"),
    version_column="ingested_at",
)


@dataclass(frozen=True, slots=True)
class IcebergCompactionReport:
    """Stage 9 Lakehouse Storage Optimization & Iceberg Snapshot Metadata report."""

    table_identifier: str
    snapshot_id: int
    files_before_compaction: int
    files_after_compaction: int
    total_rows: int
    compacted_parquet_path: str
    metadata_manifest_path: str
    compression_codec: str = "ZSTD"


class SilverLakehouseMergeEngine:
    """Executes idempotent Bronze -> Silver standardization, `MERGE INTO` deduplication, and Stage 9 compaction."""

    def __init__(self, lakehouse_root: Path | str = ".local_lakehouse") -> None:
        self._root = Path(lakehouse_root)

    def merge_bronze_klines_to_silver(
        self,
        bronze_parquet_files: list[Path],
    ) -> tuple[Path, list[dict[str, Any]]]:
        """Read Bronze kline Parquet files, deduplicate by natural key, and write Silver table."""
        deduped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
        for pq_file in bronze_parquet_files:
            if not pq_file.exists():
                continue
            table = pq.read_table(pq_file)
            for raw_row in table.to_pylist():
                if str(raw_row.get("event_type", "kline")) != "kline":
                    continue
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
        if silver_rows:
            pq.write_table(pa.Table.from_pylist(silver_rows), out_path, compression="ZSTD")
        return out_path, silver_rows

    def merge_bronze_trades_to_silver(
        self,
        bronze_parquet_files: list[Path],
    ) -> tuple[Path, list[dict[str, Any]]]:
        """Read Bronze trade Parquet files, deduplicate by `(provider, symbol, trade_id)`, and write Silver table."""
        deduped: dict[tuple[str, str, int], dict[str, Any]] = {}
        for pq_file in bronze_parquet_files:
            if not pq_file.exists():
                continue
            table = pq.read_table(pq_file)
            for raw_row in table.to_pylist():
                if str(raw_row.get("event_type", "")) != "trade":
                    continue
                payload = json.loads(str(raw_row["payload_json"]))
                trade_id = int(payload["trade_id"])
                record = {
                    "provider": str(raw_row["provider"]).lower(),
                    "symbol": str(raw_row["symbol"]).upper(),
                    "trade_id": trade_id,
                    "price": float(payload["price"]),
                    "quantity": float(payload["quantity"]),
                    "quote_volume": float(payload["quote_volume"]),
                    "is_buyer_maker": bool(payload.get("is_buyer_maker", False)),
                    "trade_time": str(payload["trade_time"]),
                    "exchange_event_time": str(raw_row["exchange_event_time"]),
                    "ingested_at": str(raw_row["ingested_at"]),
                }
                natural_key = (record["provider"], record["symbol"], record["trade_id"])
                existing = deduped.get(natural_key)
                if existing is None or record["ingested_at"] >= existing["ingested_at"]:
                    deduped[natural_key] = record

        silver_rows = sorted(
            deduped.values(),
            key=lambda r: (r["provider"], r["symbol"], r["trade_id"]),
        )
        silver_dir = self._root / "silver" / "market_trades"
        silver_dir.mkdir(parents=True, exist_ok=True)
        out_path = silver_dir / "silver_market_trades.parquet"
        if silver_rows:
            pq.write_table(pa.Table.from_pylist(silver_rows), out_path, compression="ZSTD")
        return out_path, silver_rows

    def compact_and_snapshot_iceberg_table(
        self,
        layer: str = "silver",
        table_name: str = "market_klines",
        sort_keys: tuple[str, ...] = ("provider", "symbol", "open_time"),
    ) -> IcebergCompactionReport:
        """Stage 9 (Data Storage Optimization): Compact small Parquet files and write Iceberg v2 metadata."""
        table_dir = self._root / layer / table_name
        table_dir.mkdir(parents=True, exist_ok=True)
        pq_files = sorted(p for p in table_dir.rglob("*.parquet") if p.is_file())
        files_before = len(pq_files)

        all_rows: list[dict[str, Any]] = []
        for f in pq_files:
            all_rows.extend(pq.read_table(f).to_pylist())

        if all_rows:
            all_rows.sort(key=lambda r: tuple(str(r.get(k, "")) for k in sort_keys))

        compacted_file = table_dir / f"compacted_{layer}_{table_name}.parquet"
        if all_rows:
            pq.write_table(pa.Table.from_pylist(all_rows), compacted_file, compression="ZSTD")

        # Remove fragmented part_*.parquet files if more than 1 file existed
        for f in pq_files:
            if f != compacted_file and f.name.startswith("part_"):
                f.unlink(missing_ok=True)

        remaining_files = [p for p in table_dir.rglob("*.parquet") if p.is_file()]
        digest = hashlib.sha256(f"{layer}.{table_name}:{len(all_rows)}".encode()).hexdigest()
        snapshot_id = int(digest[:12], 16)

        meta_dir = table_dir / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = meta_dir / f"v{snapshot_id}.metadata.json"
        manifest_payload = {
            "format-version": 2,
            "table-uuid": digest[:32],
            "location": str(table_dir.as_posix()),
            "table-identifier": f"lakehouse.{layer}.{table_name}",
            "current-snapshot-id": snapshot_id,
            "last-updated-ms": int(datetime.now(UTC).timestamp() * 1000),
            "properties": {
                "write.parquet.compression-codec": "zstd",
                "history.expire.max-snapshot-age-ms": "604800000",
            },
            "snapshots": [
                {
                    "snapshot-id": snapshot_id,
                    "timestamp-ms": int(datetime.now(UTC).timestamp() * 1000),
                    "summary": {
                        "operation": "replace",
                        "total-records": str(len(all_rows)),
                        "total-data-files": str(len(remaining_files)),
                    },
                }
            ],
        }
        manifest_path.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")

        return IcebergCompactionReport(
            table_identifier=f"lakehouse.{layer}.{table_name}",
            snapshot_id=snapshot_id,
            files_before_compaction=max(1, files_before),
            files_after_compaction=len(remaining_files),
            total_rows=len(all_rows),
            compacted_parquet_path=compacted_file.as_posix(),
            metadata_manifest_path=manifest_path.as_posix(),
        )
