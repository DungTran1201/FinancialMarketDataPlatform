"""Historical REST backfill orchestration worker."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ingestion.domain.ports import EventPublisherPort, HistoricalCollectorPort
from src.ingestion.infrastructure.watermark_store import IngestionWatermarkStore


class HistoricalRestBackfillWorker:
    """Executes rate-limited REST kline backfills and checkpoints durable watermarks."""

    def __init__(
        self,
        collector: HistoricalCollectorPort,
        broker: EventPublisherPort,
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
