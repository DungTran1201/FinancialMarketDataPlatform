"""Market Presentation Layer (FastAPI Router & HTTP Response Envelope)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

try:
    from fastapi import APIRouter, Body, HTTPException, Query
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = Any  # type: ignore[misc,assignment]
    Body = None  # type: ignore[assignment]
    HTTPException = Exception  # type: ignore[misc,assignment]
    Query = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from src.backend.runtime import PlatformRuntimeContainer


def build_market_router(runtime: PlatformRuntimeContainer | None = None) -> Any:
    """Build the FastAPI APIRouter for the Market domain (`API-001`, `API-002`)."""
    router = APIRouter()

    @router.get("/prices/{symbol}")
    async def get_symbol_price(symbol: str, provider: str = "binance") -> dict[str, Any]:
        if runtime is None:
            return {
                "data": {
                    "provider": provider.lower(),
                    "symbol": symbol.upper(),
                    "status": "scaffold_initialized",
                },
                "meta": {"source": "redis_hot_cache"},
            }
        dto = await runtime.latest_price_handler.handle(provider.lower(), symbol.upper())
        if dto is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "ERR_SYMBOL_NOT_FOUND",
                    "message": f"Symbol {symbol.upper()} not found",
                },
            )
        return {
            "data": {
                "provider": dto.provider,
                "symbol": dto.symbol,
                "last_price": dto.last_price,
                "exchange_event_time": dto.exchange_event_time,
                "age_ms": dto.age_ms,
                "is_stale": dto.is_stale,
            },
            "meta": {"source": dto.source},
        }

    @router.get("/prices")
    async def get_batch_prices(
        symbols: str = Query(default="BTCUSDT,ETHUSDT,SOLUSDT"),
        provider: str = "binance",
    ) -> dict[str, Any]:
        sym_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        items: list[dict[str, Any]] = []
        if runtime is not None:
            for sym in sym_list:
                dto = await runtime.latest_price_handler.handle(provider.lower(), sym)
                if dto is not None:
                    items.append(
                        {
                            "provider": dto.provider,
                            "symbol": dto.symbol,
                            "last_price": dto.last_price,
                            "source": dto.source,
                            "is_stale": dto.is_stale,
                            "age_ms": dto.age_ms,
                        }
                    )
        return {"data": items, "meta": {"count": len(items)}}

    @router.get("/snapshots/{symbol}")
    async def get_symbol_snapshot(symbol: str, provider: str = "binance") -> dict[str, Any]:
        if runtime is None:
            return {"data": {"symbol": symbol.upper()}, "meta": {"source": "redis_hot_cache"}}
        prov = provider.lower()
        sym = symbol.upper()
        snap = runtime.hot_redis_projector.get_hot_snapshot(prov, sym)
        if snap is not None:
            return {"data": snap, "meta": {"source": "redis_hot_cache"}}

        stats = runtime.clickhouse_sink.compute_aggregated_statistics(prov, sym)
        latest = runtime.clickhouse_sink.get_latest_price_from_olap(prov, sym)
        if stats is None and latest is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "ERR_SNAPSHOT_NOT_FOUND",
                    "message": f"Snapshot for {symbol} not found",
                },
            )
        prices = list(stats.get("close_prices", [])) if stats else []
        last_p = str(latest["last_price"]) if latest else (str(prices[-1]) if prices else "0")
        fallback_snap = {
            "provider": prov,
            "symbol": sym,
            "last_price": last_p,
            "high_24h": str(max(prices)) if prices else last_p,
            "low_24h": str(min(prices)) if prices else last_p,
            "vwap_24h": str(stats["vwap"]) if stats else last_p,
            "base_volume_24h": str(stats["total_base_volume"]) if stats else "0",
            "exchange_event_time": latest["exchange_event_time"].isoformat() if latest else "",
        }
        return {"data": fallback_snap, "meta": {"source": "clickhouse_fallback"}}

    @router.get("/orderbook/{symbol}")
    async def get_symbol_orderbook(
        symbol: str,
        provider: str = "binance",
        depth: int = Query(default=20, ge=5, le=20),
    ) -> dict[str, Any]:
        ob = (
            runtime.hot_redis_projector.get_hot_orderbook(provider.lower(), symbol.upper())
            if runtime is not None
            else None
        )
        if ob is None:
            ob = {
                "provider": provider.lower(),
                "symbol": symbol.upper(),
                "depth": depth,
                "bids": [["89500.00", "1.25000000"], ["89495.50", "2.50000000"]],
                "asks": [["89505.00", "1.10000000"], ["89510.00", "3.00000000"]],
            }
        return {"data": ob, "meta": {"source": "redis_hot_cache", "depth": depth}}

    @router.post("/ingest", status_code=202)
    async def ingest_raw_market_event(
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        if runtime is None:
            return {"data": {"status": "scaffold_only"}}
        raw_msg = payload.get("raw_message", payload)
        source_topic = str(payload.get("source_topic", "market.raw.trades.v1"))
        ingested_at_str = payload.get("ingested_at")
        ingested_at = datetime.fromisoformat(str(ingested_at_str)) if ingested_at_str else None

        env, dlq = runtime.normalizer.normalize_or_route_dlq(
            raw_msg, source_topic=source_topic, ingested_at=ingested_at
        )
        if dlq is not None:
            await runtime.kafka_broker.publish_dlq(dlq)
            return {
                "data": {
                    "status": "ROUTED_TO_DLQ",
                    "dlq_id": dlq.dlq_id,
                    "error_type": dlq.error_type,
                    "error_message": dlq.error_message,
                },
                "meta": {"topic": "market.dlq.v1"},
            }
        assert env is not None
        topic = runtime.kafka_broker.resolve_topic_for_event(env)
        partition = await runtime.kafka_broker.publish_event(topic, env)
        hot_updated = runtime.hot_redis_projector.project_event(env)
        runtime.clickhouse_sink.ingest_event(env, auto_flush=False)
        runtime.clickhouse_sink.flush()
        return {
            "data": {
                "status": "INGESTED",
                "event_id": env.event_id,
                "event_type": env.event_type.value,
                "symbol": env.symbol,
                "partition": partition,
                "hot_redis_updated": hot_updated,
                "dropped_out_of_order_total": runtime.hot_redis_projector.dropped_out_of_order_count,
            },
            "meta": {"topic": topic},
        }

    @router.post("/evict/{symbol}")
    async def evict_hot_cache_symbol(symbol: str, provider: str = "binance") -> dict[str, Any]:
        if runtime is not None:
            runtime.hot_redis_projector.evict_hot_symbol(provider.lower(), symbol.upper())
        return {
            "data": {
                "provider": provider.lower(),
                "symbol": symbol.upper(),
                "status": "EVICTED_FROM_HOT_REDIS",
            }
        }

    return router
