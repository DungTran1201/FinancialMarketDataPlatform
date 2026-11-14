"""Standalone Data Plane v0.1 Microservice (`svc-data-plane-v01`) & FastAPI Router."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.backend.runtime import PlatformRuntimeContainer


class RunDataPlatformV01Request(BaseModel):
    symbols: list[str] = Field(default_factory=lambda: ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    interval: str = Field(default="1m")
    backfill_minutes: int = Field(default=6, ge=2, le=120)


class TriggerCompactionRequest(BaseModel):
    layer: str = Field(default="silver")
    table_name: str = Field(default="market_klines")


def build_data_platform_v01_router(runtime: PlatformRuntimeContainer) -> APIRouter:
    """Build the `/api/v1/data-platform/v01` router exposing all 12 stages of Data Platform v0.1."""
    router = APIRouter()

    @router.post("/run")
    async def run_data_platform_v01(req: RunDataPlatformV01Request) -> dict[str, Any]:
        """Execute all 12 stages of the End-to-End Data Platform v0.1 pipeline with zero mocks."""
        report = await runtime.data_platform_v01.run_end_to_end_pipeline(
            symbols=tuple(s.upper() for s in req.symbols),
            interval=req.interval,
            backfill_minutes=req.backfill_minutes,
        )
        return report.to_dict()

    @router.get("/status")
    async def get_data_platform_v01_status() -> dict[str, Any]:
        """Return latest execution report and live stage readiness for Data Platform v0.1."""
        last_rep = runtime.data_platform_v01.last_report
        discovered = await runtime.historical_collector.discover_exchange_metadata()
        return {
            "service_id": "svc-data-plane-v01",
            "version": "0.1.0",
            "zero_mock_mode": True,
            "discovered_instruments_count": len(discovered),
            "rate_limit_used_weight": runtime.historical_collector.rate_limiter.used_weight,
            "dlq_events_count": len(runtime.kafka_broker.dlq_events),
            "watermarks_count": len(runtime.data_platform_v01.watermark_store.list_watermarks()),
            "last_execution_report": last_rep.to_dict() if last_rep else None,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    @router.get("/gold/{mart_name}")
    async def query_gold_mart(
        mart_name: str,
        symbol: str | None = Query(default=None),
    ) -> dict[str, Any]:
        """Query materialized Gold analytical marts (`fct_daily_market_summary`, `fct_realized_volatility`, etc.)."""
        allowed = {
            "fct_daily_market_summary",
            "fct_realized_volatility",
            "fct_orderbook_liquidity",
        }
        clean = mart_name.replace("gold.", "")
        if clean not in allowed:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown Gold mart '{mart_name}'. Allowed: {sorted(allowed)}",
            )
        rows = runtime.data_platform_v01.gold_mart_engine.query_gold_mart(clean, symbol=symbol)
        return {
            "mart_name": f"gold.{clean}",
            "symbol_filter": symbol.upper() if symbol else None,
            "row_count": len(rows),
            "rows": rows,
        }

    @router.post("/compaction")
    async def trigger_lakehouse_compaction(req: TriggerCompactionRequest) -> dict[str, Any]:
        """Execute Stage 9 small-file Parquet compaction and generate Iceberg v2 snapshot manifest."""
        sort_keys = (
            ("provider", "symbol", "trade_id")
            if "trade" in req.table_name
            else ("provider", "symbol", "open_time")
        )
        rep = runtime.silver_merge_engine.compact_and_snapshot_iceberg_table(
            layer=req.layer,
            table_name=req.table_name,
            sort_keys=sort_keys,
        )
        return {
            "table_identifier": rep.table_identifier,
            "snapshot_id": rep.snapshot_id,
            "files_before_compaction": rep.files_before_compaction,
            "files_after_compaction": rep.files_after_compaction,
            "total_rows": rep.total_rows,
            "compacted_parquet_path": rep.compacted_parquet_path,
            "metadata_manifest_path": rep.metadata_manifest_path,
            "compression_codec": rep.compression_codec,
        }

    @router.get("/lineage")
    async def get_governance_lineage() -> dict[str, Any]:
        """Return Stage 12 dataset ownership, retention policies, and end-to-end lineage graph."""
        return runtime.data_platform_v01.lineage_registry.export_lineage_catalog()

    @router.get("/watermarks")
    async def list_ingestion_watermarks() -> dict[str, Any]:
        """Return durable ingestion watermarks recorded by `collector-rest`."""
        records = runtime.data_platform_v01.watermark_store.list_watermarks()
        return {
            "count": len(records),
            "watermarks": [
                {
                    "provider": r.provider,
                    "symbol": r.symbol,
                    "interval": r.interval,
                    "last_open_time": r.last_open_time.isoformat(),
                    "updated_at": r.updated_at.isoformat(),
                    "status": r.status,
                }
                for r in records
            ],
        }

    @router.get("/metrics", response_class=PlainTextResponse)
    async def export_prometheus_metrics() -> str:
        """Export Stage 11 OpenMetrics / Prometheus exposition text (`fmdp_*`)."""
        return runtime.data_platform_v01.observability.export_prometheus_text()

    return router


def create_data_plane_microservice_app(runtime: PlatformRuntimeContainer | None = None) -> FastAPI:
    """Create standalone FastAPI application for `svc-data-plane-v01` (port 8007)."""
    from src.backend.runtime import PlatformRuntimeContainer

    rt = runtime or PlatformRuntimeContainer()
    app = FastAPI(title="Data Platform v0.1 Microservice (svc-data-plane-v01)", version="0.1.0")
    app.state.runtime = rt

    @app.get("/api/v1/health/live")
    async def health_live() -> dict[str, Any]:
        return {
            "status": "alive",
            "service_id": "svc-data-plane-v01",
            "plane": "Plane A (Data Plane)",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    app.include_router(
        build_data_platform_v01_router(runtime=rt),
        prefix="/api/v1/data-platform/v01",
        tags=["Data Platform v0.1 (End-to-End 12 Stages)"],
    )
    return app
