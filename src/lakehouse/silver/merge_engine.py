"""PySpark Batch Job Specification, Silver Iceberg Deduplication & Compaction Engine (Bronze -> Silver).

Enforces Financial Precision Invariant (BR-001): all prices, quantities, and volumes are normalized
and persisted using exact fixed-point `Decimal` strings (`0.00000001`), never binary `float`.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

DECIMAL_8 = Decimal("0.00000001")


def _fmt_dec(val: Any) -> str:
    """Format a numeric or string value as an exact 8-decimal fixed-point string."""
    return str(Decimal(str(val)).quantize(DECIMAL_8))


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
    parent_snapshot_id: int | None
    files_before_compaction: int
    files_after_compaction: int
    rows_before_dedup: int
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
        """Read Bronze kline Parquet files, deduplicate by natural key with Decimal, and write Silver."""
        silver_dir = self._root / "silver" / "market_klines"
        silver_dir.mkdir(parents=True, exist_ok=True)

        deduped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
        # Load existing Silver rows first so incremental merges preserve prior deduplicated state
        for existing_pq in sorted(silver_dir.glob("*.parquet")):
            for row in pq.read_table(existing_pq).to_pylist():
                nkey = (
                    str(row["provider"]).lower(),
                    str(row["symbol"]).upper(),
                    str(row["interval"]),
                    str(row["open_time"]),
                )
                deduped[nkey] = {
                    "provider": nkey[0],
                    "symbol": nkey[1],
                    "interval": nkey[2],
                    "open_time": nkey[3],
                    "close_time": str(row["close_time"]),
                    "open_price": _fmt_dec(row["open_price"]),
                    "high_price": _fmt_dec(row["high_price"]),
                    "low_price": _fmt_dec(row["low_price"]),
                    "close_price": _fmt_dec(row["close_price"]),
                    "base_volume": _fmt_dec(row["base_volume"]),
                    "quote_volume": _fmt_dec(row["quote_volume"]),
                    "trade_count": int(row.get("trade_count", 0)),
                    "is_closed": bool(row.get("is_closed", True)),
                    "exchange_event_time": str(row["exchange_event_time"]),
                    "ingested_at": str(row["ingested_at"]),
                }

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
                    "open_price": _fmt_dec(payload["open_price"]),
                    "high_price": _fmt_dec(payload["high_price"]),
                    "low_price": _fmt_dec(payload["low_price"]),
                    "close_price": _fmt_dec(payload["close_price"]),
                    "base_volume": _fmt_dec(payload["base_volume"]),
                    "quote_volume": _fmt_dec(payload["quote_volume"]),
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
        out_path = silver_dir / "silver_market_klines.parquet"
        if silver_rows:
            pq.write_table(pa.Table.from_pylist(silver_rows), out_path, compression="ZSTD")
        return out_path, silver_rows

    def merge_bronze_trades_to_silver(
        self,
        bronze_parquet_files: list[Path],
    ) -> tuple[Path, list[dict[str, Any]]]:
        """Read Bronze trade Parquet files, deduplicate by `(provider, symbol, trade_id)` with Decimal precision."""
        silver_dir = self._root / "silver" / "market_trades"
        silver_dir.mkdir(parents=True, exist_ok=True)

        deduped: dict[tuple[str, str, int], dict[str, Any]] = {}
        for existing_pq in sorted(silver_dir.glob("*.parquet")):
            for row in pq.read_table(existing_pq).to_pylist():
                nkey = (
                    str(row["provider"]).lower(),
                    str(row["symbol"]).upper(),
                    int(row["trade_id"]),
                )
                deduped[nkey] = {
                    "provider": nkey[0],
                    "symbol": nkey[1],
                    "trade_id": nkey[2],
                    "price": _fmt_dec(row["price"]),
                    "quantity": _fmt_dec(row["quantity"]),
                    "quote_volume": _fmt_dec(row["quote_volume"]),
                    "is_buyer_maker": bool(row.get("is_buyer_maker", False)),
                    "trade_time": str(row["trade_time"]),
                    "exchange_event_time": str(row["exchange_event_time"]),
                    "ingested_at": str(row["ingested_at"]),
                }

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
                    "price": _fmt_dec(payload["price"]),
                    "quantity": _fmt_dec(payload["quantity"]),
                    "quote_volume": _fmt_dec(payload["quote_volume"]),
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
        out_path = silver_dir / "silver_market_trades.parquet"
        if silver_rows:
            pq.write_table(pa.Table.from_pylist(silver_rows), out_path, compression="ZSTD")
        return out_path, silver_rows

    def compact_and_snapshot_iceberg_table(
        self,
        layer: str = "silver",
        table_name: str = "market_klines",
        sort_keys: tuple[str, ...] = ("provider", "symbol", "open_time"),
        max_snapshots_to_keep: int = 5,
    ) -> IcebergCompactionReport:
        """Stage 9 (Data Storage Optimization): Deduplicate by natural key, compact all Parquet files
        into a single ZSTD file, and maintain cumulative Apache Iceberg v2 snapshot history.
        """
        table_dir = self._root / layer / table_name
        table_dir.mkdir(parents=True, exist_ok=True)
        pq_files = sorted(p for p in table_dir.glob("*.parquet") if p.is_file())
        files_before = len(pq_files)

        raw_rows: list[dict[str, Any]] = []
        for f in pq_files:
            raw_rows.extend(pq.read_table(f).to_pylist())
        rows_before_dedup = len(raw_rows)

        # Determine natural key & version column for idempotent deduplication during compaction
        if "trade" in table_name:
            nat_cols = SILVER_TRADES_MERGE_SPEC.natural_key_columns
            ver_col = SILVER_TRADES_MERGE_SPEC.version_column
        elif "kline" in table_name:
            nat_cols = SILVER_KLINES_MERGE_SPEC.natural_key_columns
            ver_col = SILVER_KLINES_MERGE_SPEC.version_column
        else:
            nat_cols = sort_keys
            ver_col = "ingested_at"

        deduped_map: dict[tuple[Any, ...], dict[str, Any]] = {}
        for row in raw_rows:
            nkey = tuple(row.get(c) for c in nat_cols)
            existing = deduped_map.get(nkey)
            if existing is None or str(row.get(ver_col, "")) >= str(existing.get(ver_col, "")):
                deduped_map[nkey] = row

        deduped_rows = sorted(
            deduped_map.values(),
            key=lambda r: tuple(str(r.get(k, "")) for k in sort_keys),
        )

        compacted_file = table_dir / f"compacted_{layer}_{table_name}.parquet"
        staging_file = table_dir / f".staging_compacted_{layer}_{table_name}.parquet"

        if deduped_rows:
            pq.write_table(pa.Table.from_pylist(deduped_rows), staging_file, compression="ZSTD")
            # Remove ALL prior uncompacted and compacted Parquet files so only the single compacted file remains
            for f in pq_files:
                f.unlink(missing_ok=True)
            staging_file.replace(compacted_file)

        remaining_files = [p for p in table_dir.glob("*.parquet") if p.is_file()]

        meta_dir = table_dir / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)
        hint_path = meta_dir / "version-hint.text"
        prior_snapshots: list[dict[str, Any]] = []
        parent_snapshot_id: int | None = None
        latest_manifest_file: Path | None = None
        if hint_path.exists():
            hint_id = hint_path.read_text(encoding="utf-8").strip()
            candidate = meta_dir / f"v{hint_id}.metadata.json"
            if candidate.exists():
                latest_manifest_file = candidate
        if latest_manifest_file is None:
            prior_manifests = sorted(
                meta_dir.glob("v*.metadata.json"), key=lambda p: p.stat().st_mtime_ns
            )
            if prior_manifests:
                latest_manifest_file = prior_manifests[-1]
        if latest_manifest_file is not None:
            try:
                latest_meta = json.loads(latest_manifest_file.read_text(encoding="utf-8"))
                prior_snapshots = list(latest_meta.get("snapshots", []))
                parent_snapshot_id = latest_meta.get("current-snapshot-id")
            except Exception:
                prior_snapshots = []

        now_ms = int(datetime.now(UTC).timestamp() * 1000)
        digest_input = f"{layer}.{table_name}:{len(deduped_rows)}:{len(prior_snapshots) + 1}:{now_ms}"
        digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()
        snapshot_id = int(digest[:12], 16)

        new_snapshot_entry = {
            "snapshot-id": snapshot_id,
            "parent-snapshot-id": parent_snapshot_id,
            "timestamp-ms": now_ms,
            "summary": {
                "operation": "replace",
                "rows-before-dedup": str(rows_before_dedup),
                "total-records": str(len(deduped_rows)),
                "total-data-files": str(len(remaining_files)),
            },
        }
        retained_snapshots = (prior_snapshots + [new_snapshot_entry])[-max_snapshots_to_keep:]

        manifest_path = meta_dir / f"v{snapshot_id}.metadata.json"
        manifest_payload = {
            "format-version": 2,
            "table-uuid": hashlib.sha256(f"uuid:{layer}.{table_name}".encode()).hexdigest()[:32],
            "location": str(table_dir.as_posix()),
            "table-identifier": f"lakehouse.{layer}.{table_name}",
            "current-snapshot-id": snapshot_id,
            "last-updated-ms": now_ms,
            "properties": {
                "write.parquet.compression-codec": "zstd",
                "history.expire.max-snapshot-age-ms": "604800000",
            },
            "snapshots": retained_snapshots,
        }
        manifest_path.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")
        (meta_dir / "version-hint.text").write_text(str(snapshot_id), encoding="utf-8")

        # Expire old metadata JSON files beyond max_snapshots_to_keep
        all_manifests = sorted(meta_dir.glob("v*.metadata.json"))
        for old_m in all_manifests[:-max_snapshots_to_keep]:
            old_m.unlink(missing_ok=True)

        return IcebergCompactionReport(
            table_identifier=f"lakehouse.{layer}.{table_name}",
            snapshot_id=snapshot_id,
            parent_snapshot_id=parent_snapshot_id,
            files_before_compaction=max(1, files_before),
            files_after_compaction=len(remaining_files),
            rows_before_dedup=rows_before_dedup,
            total_rows=len(deduped_rows),
            compacted_parquet_path=compacted_file.as_posix(),
            metadata_manifest_path=manifest_path.as_posix(),
        )
