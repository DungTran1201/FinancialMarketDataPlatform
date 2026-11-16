"""Bronze Layer Immutable Parquet Archiver (`bronze/` partition writer, Stage 5)."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from src.shared.contracts.events.market_events import EventEnvelopeV1


def build_bronze_partition_path(provider: str, event_type: str, ingestion_date: str) -> str:
    """Return canonical Hive/Iceberg-compatible Bronze object storage path."""
    return f"bronze/{event_type}/provider={provider.lower()}/ingestion_date={ingestion_date}"


class BronzeParquetArchiver:
    """Writes immutable raw `EventEnvelopeV1` batches to ZSTD-compressed Parquet files in Bronze."""

    CONSUMER_GROUP = "cg.lakehouse.bronze.v1"

    def __init__(self, lakehouse_root: Path | str = ".local_lakehouse") -> None:
        self._root = Path(lakehouse_root)

    def archive_batch(
        self,
        events: list[EventEnvelopeV1],
        batch_id: str = "0001",
    ) -> list[Path]:
        """Group events by `(provider, event_type, ingestion_date)` and write ZSTD Parquet files."""
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for ev in events:
            ing_date = ev.ingested_at.strftime("%Y-%m-%d")
            key = (ev.provider.lower(), ev.event_type.value, ing_date)
            grouped.setdefault(key, []).append(
                {
                    "event_id": str(ev.event_id),
                    "schema_version": ev.schema_version,
                    "provider": ev.provider.lower(),
                    "symbol": ev.symbol.upper(),
                    "event_type": ev.event_type.value,
                    "exchange_event_time": ev.exchange_event_time.isoformat(),
                    "ingested_at": ev.ingested_at.isoformat(),
                    "partition_key": ev.partition_key,
                    "payload_json": json.dumps(ev.payload, sort_keys=True),
                }
            )

        written_files: list[Path] = []
        for (provider, event_type, ing_date), rows in grouped.items():
            rel_dir = build_bronze_partition_path(provider, event_type, ing_date)
            out_dir = self._root / rel_dir
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"part_{event_type}_{batch_id}.parquet"
            table = pa.Table.from_pylist(rows)
            tmp_file = out_file.with_name(
                f".{out_file.name}.{os.getpid()}.{uuid.uuid4().hex[:8]}.tmp"
            )
            try:
                pq.write_table(table, tmp_file, compression="ZSTD")
                tmp_file.replace(out_file)
            except Exception:
                tmp_file.unlink(missing_ok=True)
                raise
            written_files.append(out_file)

        return written_files
