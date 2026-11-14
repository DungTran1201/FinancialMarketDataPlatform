"""Standalone Real-Time Market Hot-State Microservice (`svc-market-hot`, Port 8001)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI

if TYPE_CHECKING:
    from src.backend.runtime import PlatformRuntimeContainer


def create_market_microservice_app(runtime: PlatformRuntimeContainer | None = None) -> FastAPI:
    """Create standalone FastAPI application for `svc-market-hot` (port 8001)."""
    from src.backend.modules.market.presentation.router import build_market_router
    from src.backend.runtime import PlatformRuntimeContainer

    rt = runtime or PlatformRuntimeContainer()
    app = FastAPI(title="Market Hot-State Microservice (svc-market-hot)", version="0.1.0")
    app.state.runtime = rt

    @app.get("/api/v1/health/live")
    async def health_live() -> dict[str, Any]:
        return {
            "status": "alive",
            "service_id": "svc-market-hot",
            "bounded_context": "market",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    app.include_router(
        build_market_router(runtime=rt),
        prefix="/api/v1/market",
        tags=["Market Hot-State & Fallback"],
    )
    return app

