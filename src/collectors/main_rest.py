"""Historical REST Backfill & Watermark Checkpointing Worker (Plane A: `collector-rest`)."""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.collectors.publisher import (
    PartitionedEventStreamingBroker,
    ProductionExchangeHistoricalCollector,
)
from src.shared.config import PlatformConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class WatermarkRecord:
    """Durable ingestion watermark checkpoint record (`ingestion_watermarks` control table)."""

    provider: str
    symbol: str
    interval: str
    last_open_time: datetime
    updated_at: datetime
    status: str  # SYNCED | BACKFILLING | GAP_DETECTED


class IngestionWatermarkStore:
    """Durable SQLite/PostgreSQL-compatible control store for `ingestion_watermarks`."""

    def __init__(self, db_path: Path | str = ":memory:") -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self) -> None:
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


class HistoricalRestBackfillWorker:
    """Executes rate-limited REST kline backfills and checkpoints durable watermarks."""

    def __init__(
        self,
        collector: ProductionExchangeHistoricalCollector,
        broker: PartitionedEventStreamingBroker,
        watermark_store: IngestionWatermarkStore | None = None,
    ) -> None:
        self.collector = collector
        self.broker = broker
        self.watermark_store = watermark_store or IngestionWatermarkStore()

    async def execute_backfill(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> dict[str, Any]:
        """Fetch historical klines via production HTTP collector, publish to Kafka, and update watermark."""
        sym = symbol.upper()
        self.watermark_store.upsert_watermark(
            provider="binance",
            symbol=sym,
            interval=interval,
            last_open_time=start_time,
            status="BACKFILLING",
        )
        events = await self.collector.fetch_historical_klines(
            symbol=sym,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
        for ev in events:
            topic = self.broker.resolve_topic_for_event(ev)
            await self.broker.publish_event(topic, ev)

        final_open_time = (
            datetime.fromisoformat(str(events[-1].payload["open_time"])) if events else end_time
        )
        wm = self.watermark_store.upsert_watermark(
            provider="binance",
            symbol=sym,
            interval=interval,
            last_open_time=final_open_time,
            status="SYNCED",
        )
        return {
            "symbol": sym,
            "interval": interval,
            "events_published": len(events),
            "watermark": wm.last_open_time.isoformat(),
            "status": wm.status,
            "rate_limit_used_weight": self.collector.rate_limiter.used_weight,
        }


def main() -> None:
    config = PlatformConfig()
    logging.basicConfig(level=config.log_level)
    logger.info(
        "Initialized collector-rest backfill worker for provider=%s",
        config.default_provider,
    )


if __name__ == "__main__":
    main()
