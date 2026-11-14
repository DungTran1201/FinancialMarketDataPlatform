"""Standalone Catalog, Freshness & Platform Config Microservice (`svc-catalog-governance`, Port 8004)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI

if TYPE_CHECKING:
    from src.backend.runtime import PlatformRuntimeContainer


def create_catalog_microservice_app(runtime: PlatformRuntimeContainer | None = None) -> FastAPI:
    """Create standalone FastAPI application for `svc-catalog-governance` (port 8004)."""
    from src.backend.modules.catalog.presentation.router import build_catalog_router
    from src.backend.modules.platform_config.presentation.router import (
        build_platform_config_router,
    )
    from src.backend.runtime import PlatformRuntimeContainer

    rt = runtime or PlatformRuntimeContainer()
    app = FastAPI(title="Catalog & Governance Microservice (svc-catalog-governance)", version="0.1.0")
    app.state.runtime = rt

    @app.get("/api/v1/health/live")
    async def health_live() -> dict[str, Any]:
        return {
            "status": "alive",
            "service_id": "svc-catalog-governance",
            "bounded_contexts": ["catalog", "platform_config"],
            "timestamp": datetime.now(UTC).isoformat(),
        }

    app.include_router(
        build_catalog_router(runtime=rt),
        prefix="/api/v1/catalog",
        tags=["Data Catalog & Freshness"],
    )
    app.include_router(
        build_platform_config_router(runtime=rt),
        prefix="/api/v1/platform",
        tags=["Platform Configuration"],
    )
    return app

