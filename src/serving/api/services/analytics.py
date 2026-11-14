"""Standalone Quantitative Analytics Microservice (`svc-analytics-quant`, Port 8003)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI

if TYPE_CHECKING:
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer


def create_analytics_microservice_app(runtime: PlatformRuntimeContainer | None = None) -> FastAPI:
    """Create standalone FastAPI application for `svc-analytics-quant` (port 8003)."""
    from src.serving.api.modules.analytics.presentation.router import build_analytics_router
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer

    rt = runtime or PlatformRuntimeContainer()
    app = FastAPI(title="Quantitative Analytics Microservice (svc-analytics-quant)", version="0.1.0")
    app.state.runtime = rt

    @app.get("/api/v1/health/live")
    async def health_live() -> dict[str, Any]:
        return {
            "status": "alive",
            "service_id": "svc-analytics-quant",
            "bounded_context": "analytics",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    app.include_router(
        build_analytics_router(runtime=rt),
        prefix="/api/v1/analytics",
        tags=["Quantitative Analytics, Correlations & Anomalies"],
    )
    return app
