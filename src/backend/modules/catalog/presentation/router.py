"""Data Catalog & Freshness Presentation Layer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.backend.modules.platform_config.domain.ports import MonitoredInstrumentConfig

try:
    from fastapi import APIRouter, Body
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = Any  # type: ignore[misc,assignment]
    Body = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from src.backend.runtime import PlatformRuntimeContainer


def build_catalog_router(runtime: PlatformRuntimeContainer) -> Any:
    """Build the FastAPI APIRouter for the Data Catalog & Freshness domain."""
    router = APIRouter()

    @router.get("/instruments")
    async def list_instruments() -> dict[str, Any]:
        items = [
            {
                "provider": cfg.provider,
                "symbol": cfg.symbol,
                "enabled_streams": list(cfg.enabled_streams),
                "is_active": cfg.is_active,
            }
            for cfg in runtime.monitored_instruments.values()
        ]
        return {"data": items, "meta": {"count": len(items)}}

    @router.put("/instruments/{symbol}")
    async def upsert_instrument(
        symbol: str,
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        sym = symbol.upper()
        provider = str(payload.get("provider", "binance")).lower()
        streams = tuple(str(s) for s in payload.get("enabled_streams", ["trade", "kline_1m", "ticker"]))
        is_active = bool(payload.get("is_active", True))
        cfg = MonitoredInstrumentConfig(
            provider=provider,
            symbol=sym,
            enabled_streams=streams,
            is_active=is_active,
        )
        runtime.monitored_instruments[sym] = cfg
        return {
            "data": {
                "provider": cfg.provider,
                "symbol": cfg.symbol,
                "enabled_streams": list(cfg.enabled_streams),
                "is_active": cfg.is_active,
            }
        }

    @router.get("/freshness")
    async def get_catalog_freshness(provider: str = "binance") -> dict[str, Any]:
        reports = []
        for sym in runtime.monitored_instruments:
            rep = await runtime.get_freshness_report(provider.lower(), sym)
            reports.append(
                {
                    "provider": rep.instrument.provider,
                    "symbol": rep.instrument.symbol,
                    "hot_redis_lag_ms": rep.hot_redis_lag_ms,
                    "clickhouse_lag_ms": rep.clickhouse_lag_ms,
                    "is_healthy": rep.is_healthy,
                }
            )
        return {
            "data": reports,
            "meta": {"staleness_threshold_ms": runtime.config.market_staleness_threshold_ms},
        }

    @router.post("/lakehouse/pipeline")
    async def run_lakehouse_medallion_pipeline(
        payload: dict[str, Any] = Body(default={}),
    ) -> dict[str, Any]:
        batch_id = str(payload.get("batch_id", "bot_batch"))
        polled = runtime.kafka_broker.poll_topic(
            runtime.bronze_archiver.CONSUMER_GROUP, "market.raw.klines.v1", max_records=500
        )
        if not polled:
            polled = [
                item["envelope"]
                for item in runtime.kafka_broker._topics.get("market.raw.klines.v1", [])
                if "envelope" in item
            ]
        else:
            runtime.kafka_broker.commit_offsets(
                runtime.bronze_archiver.CONSUMER_GROUP, "market.raw.klines.v1", len(polled)
            )

        bronze_files = runtime.bronze_archiver.archive_batch(polled, batch_id=batch_id)
        if bronze_files:
            silver_path, silver_rows = runtime.silver_merge_engine.merge_bronze_klines_to_silver(bronze_files)
            dq_res = runtime.quality_gate_engine.validate_kline_dataset(silver_rows)
            return {
                "data": {
                    "batch_id": batch_id,
                    "bronze_files_written": len(bronze_files),
                    "silver_table_path": str(silver_path),
                    "silver_deduplicated_rows": len(silver_rows),
                    "dq_passed": dq_res.passed,
                    "can_promote_to_gold": dq_res.can_promote_to_gold,
                    "failed_rule_ids": list(dq_res.failed_rule_ids),
                }
            }
        return {
            "data": {
                "batch_id": batch_id,
                "bronze_files_written": 0,
                "silver_deduplicated_rows": 0,
                "dq_passed": True,
                "can_promote_to_gold": True,
                "failed_rule_ids": [],
            }
        }

    return router
