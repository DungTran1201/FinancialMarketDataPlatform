"""Durable SQLite WAL ingestion watermark repository."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from src.ingestion.domain.models import WatermarkRecord


class IngestionWatermarkStore:
    """Durable on-disk SQLite/PostgreSQL-compatible control store for `ingestion_watermarks`."""

    DEFAULT_DB_PATH = Path(".local_storage/control_watermarks.db")

    def __init__(self, db_path: Path | str | None = None) -> None:
        resolved = db_path if db_path is not None else self.DEFAULT_DB_PATH
        self._db_path = str(resolved)
        if self._db_path != ":memory:":
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self) -> None:
        if self._db_path != ":memory:":
            self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingestion_watermarks (
                provider TEXT NOT NULL,
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                last_open_time TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                status TEXT NOT NULL,
                PRIMARY KEY (provider, symbol, interval)
            )
            """
        )
        self._conn.commit()

    def upsert_watermark(
        self,
        provider: str,
        symbol: str,
        interval: str,
        last_open_time: datetime,
        status: str = "SYNCED",
    ) -> WatermarkRecord:
        now = datetime.now(UTC)
        rec = WatermarkRecord(
            provider=provider.lower(),
            symbol=symbol.upper(),
            interval=interval,
            last_open_time=last_open_time.astimezone(UTC),
            updated_at=now,
            status=status,
        )
        self._conn.execute(
            """
            INSERT INTO ingestion_watermarks (provider, symbol, interval, last_open_time, updated_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider, symbol, interval) DO UPDATE SET
                last_open_time = excluded.last_open_time,
                updated_at = excluded.updated_at,
                status = excluded.status
            """,
            (
                rec.provider,
                rec.symbol,
                rec.interval,
                rec.last_open_time.isoformat(),
                rec.updated_at.isoformat(),
                rec.status,
            ),
        )
        self._conn.commit()
        return rec

    def get_watermark(self, provider: str, symbol: str, interval: str) -> WatermarkRecord | None:
        cur = self._conn.execute(
            """
            SELECT provider, symbol, interval, last_open_time, updated_at, status
            FROM ingestion_watermarks
            WHERE provider = ? AND symbol = ? AND interval = ?
            """,
            (provider.lower(), symbol.upper(), interval),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return WatermarkRecord(
            provider=row[0],
            symbol=row[1],
            interval=row[2],
            last_open_time=datetime.fromisoformat(row[3]),
            updated_at=datetime.fromisoformat(row[4]),
            status=row[5],
        )

    def list_watermarks(self) -> list[WatermarkRecord]:
        cur = self._conn.execute(
            """
            SELECT provider, symbol, interval, last_open_time, updated_at, status
            FROM ingestion_watermarks
            ORDER BY provider, symbol, interval
            """
        )
        return [
            WatermarkRecord(
                provider=r[0],
                symbol=r[1],
                interval=r[2],
                last_open_time=datetime.fromisoformat(r[3]),
                updated_at=datetime.fromisoformat(r[4]),
                status=r[5],
            )
            for r in cur.fetchall()
        ]

    def close(self) -> None:
        """Close the underlying SQLite connection handle cleanly."""
        self._conn.close()
