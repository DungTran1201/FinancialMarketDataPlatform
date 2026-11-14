"""Historical Market Data Presentation Layer (`API-004`, `API-005`, `API-006`)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from src.shared.domain.primitives import BoundedTimeRange, DomainError

try:
    from fastapi import APIRouter, Body, HTTPException, Query, Response
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = Any  # type: ignore[misc,assignment]
    Body = None  # type: ignore[assignment]
    HTTPException = Exception  # type: ignore[misc,assignment]
    Query = None  # type: ignore[assignment]
    Response = Any  # type: ignore[misc,assignment]

if TYPE_CHECKING:
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer


def build_historical_router(runtime: PlatformRuntimeContainer) -> Any:
    """Build the FastAPI APIRouter for Historical OHLCV, Trades & Backfill Jobs."""
    router = APIRouter()

    @router.get("/klines/{symbol}")
    async def get_historical_klines(
        symbol: str,
        provider: str = "binance",
        interval: str = "1m",
        start_time: str | None = None,
        end_time: str | None = None,
        max_window_days: int = Query(default=30, ge=1, le=365),
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        dt_end = datetime.fromisoformat(end_time) if end_time else now
        dt_start = datetime.fromisoformat(start_time) if start_time else dt_end - timedelta(hours=2)
        try:
            bounded_range = BoundedTimeRange(
                start_time=dt_start,
                end_time=dt_end,
                max_span_seconds=max_window_days * 86400,
            )
        except (DomainError, ValueError) as exc:
            raise HTTPException(
                status_code=422,
                detail={"code": "ERR_INVALID_TIME_RANGE", "message": str(exc)},
            ) from exc

        candles = runtime.query_historical_candles(
            provider=provider.lower(),
            symbol=symbol.upper(),
            interval=interval,
            time_range=bounded_range,
            limit=limit,
        )
        return {
            "data": [
                {
                    "provider": c.instrument.provider,
                    "symbol": c.instrument.symbol,
                    "interval": c.interval,
                    "open_time": c.open_time.isoformat(),
                    "close_time": c.close_time.isoformat(),
                    "open_price": str(c.open_price),
                    "high_price": str(c.high_price),
                    "low_price": str(c.low_price),
                    "close_price": str(c.close_price),
                    "base_volume": str(c.base_volume),
                    "quote_volume": str(c.quote_volume),
                    "trade_count": c.trade_count,
                }
                for c in candles
            ],
            "meta": {
                "source": "clickhouse_olap",
                "count": len(candles),
                "window_start": bounded_range.start_time.isoformat(),
                "window_end": bounded_range.end_time.isoformat(),
            },
        }

    @router.get("/trades/{symbol}")
    async def get_historical_trades(
        symbol: str,
        provider: str = "binance",
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> dict[str, Any]:
        prov = provider.lower()
        sym = symbol.upper()
        rows = [
            {
                "provider": r["provider"],
                "symbol": r["symbol"],
                "trade_id": r["trade_id"],
                "price": str(r["price"]),
                "quantity": str(r["quantity"]),
                "quote_volume": str(r["quote_volume"]),
                "exchange_event_time": r["exchange_event_time"].isoformat(),
            }
            for (p, s, _), r in runtime.clickhouse_sink._trades_table.items()
            if p == prov and s == sym
        ][:limit]
        return {"data": rows, "meta": {"source": "clickhouse_olap", "count": len(rows)}}

    @router.post("/backfill-jobs", status_code=202)
    async def trigger_backfill_job(
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        symbol = str(payload.get("symbol", "BTCUSDT")).upper()
        provider = str(payload.get("provider", "binance")).lower()
        interval = str(payload.get("interval", "1m"))
        candle_count = int(payload.get("candle_count", 10))
        start_time_str = payload.get("start_time")
        now_dt = datetime.now(UTC)
        start_dt = (
            datetime.fromisoformat(start_time_str) if start_time_str else now_dt - timedelta(minutes=candle_count)
        )
        end_dt = start_dt + timedelta(minutes=candle_count if interval == "1m" else candle_count * 60)

        job_id = f"bf_{uuid.uuid4().hex[:10]}"
        envelopes = await runtime.historical_collector.fetch_historical_klines(
            symbol=symbol,
            interval=interval,
            start_time=start_dt,
            end_time=end_dt,
            limit=candle_count,
        )
        for env in envelopes:
            await runtime.kafka_broker.publish_event("market.raw.klines.v1", env)
            runtime.hot_redis_projector.project_event(env)
            runtime.clickhouse_sink.ingest_event(env, auto_flush=False)
        runtime.clickhouse_sink.flush()
        runtime.bronze_archiver.archive_batch(envelopes, batch_id=job_id)

        watermark = envelopes[-1].exchange_event_time if envelopes else start_dt
        runtime.ingestion_watermarks[f"{provider}:{symbol}:{interval}"] = watermark
        job_record = {
            "job_id": job_id,
            "provider": provider,
            "symbol": symbol,
            "interval": interval,
            "status": "COMPLETED",
            "ingested_candles": len(envelopes),
            "watermark_time": watermark.isoformat(),
            "created_at": datetime.now(UTC).isoformat(),
            "transport_mode": "MOCKED_SIMULATED_EXCHANGE_REST",
        }
        runtime.backfill_jobs[job_id] = job_record
        return {"data": job_record, "meta": {"idempotent_merge": "ReplacingMergeTree"}}

    @router.get("/backfill-jobs/{job_id}")
    async def get_backfill_job_status(job_id: str) -> dict[str, Any]:
        job = runtime.backfill_jobs.get(job_id)
        if job is None:
            raise HTTPException(
                status_code=404,
                detail={"code": "ERR_JOB_NOT_FOUND", "message": f"Backfill job {job_id} not found"},
            )
        return {"data": job}

    return router
