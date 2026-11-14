"""Standalone Historical OLAP & Backfill Microservice (`svc-historical-backfill`, Port 8002)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI

if TYPE_CHECKING:
    from src.backend.runtime import PlatformRuntimeContainer


def create_historical_microservice_app(runtime: PlatformRuntimeContainer | None = None) -> FastAPI:
    """Create standalone FastAPI application for `svc-historical-backfill` (port 8002)."""
    from src.backend.modules.historical.presentation.router import build_historical_router
    from src.backend.runtime import PlatformRuntimeContainer

    rt = runtime or PlatformRuntimeContainer()
    app = FastAPI(title="Historical OLAP & Backfill Microservice (svc-historical-backfill)", version="0.1.0")
    app.state.runtime = rt

    @app.get("/api/v1/health/live")
    async def health_live() -> dict[str, Any]:
        return {
            "status": "alive",
            "service_id": "svc-historical-backfill",
            "bounded_context": "historical",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    app.include_router(
        build_historical_router(runtime=rt),
        prefix="/api/v1/historical",
        tags=["Historical OHLCV, Trades & Backfills"],
    )
    return app

