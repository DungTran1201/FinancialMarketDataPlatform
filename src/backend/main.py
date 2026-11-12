"""FastAPI Modular Monolith Application Entrypoint & Health Checks (Plane B)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.shared.config import PlatformConfig


def get_liveness_status() -> dict[str, Any]:
    """Minimal liveness probe payload (verifies process responsiveness)."""
    config = PlatformConfig()
    return {
        "status": "alive",
        "service": "backend-api",
        "environment": config.app_env,
        "timestamp": datetime.now(UTC).isoformat(),
    }


def get_readiness_status() -> dict[str, Any]:
    """Minimal readiness probe payload reporting configured plane dependencies."""
    config = PlatformConfig()
    return {
        "status": "ready",
        "service": "backend-api",
        "dependencies": {
            "redis": f"{config.redis_host}:{config.redis_port}",
            "clickhouse": f"{config.clickhouse_host}:{config.clickhouse_http_port}",
            "postgres": f"{config.postgres_host}:{config.postgres_port}",
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }


def create_app() -> Any:
    """Create the FastAPI Modular Monolith application when FastAPI is installed."""
    from fastapi import FastAPI

    from src.backend.modules.market.presentation.router import build_market_router

    app = FastAPI(
        title="Real-time Financial Market Data Platform API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    @app.get("/api/v1/health/live", tags=["Health"])
    async def health_live() -> dict[str, Any]:
        return get_liveness_status()

    @app.get("/api/v1/health/ready", tags=["Health"])
    async def health_ready() -> dict[str, Any]:
        return get_readiness_status()

    app.include_router(build_market_router(), prefix="/api/v1/market", tags=["Market"])
    return app


try:
    app = create_app()
except ModuleNotFoundError:  # Allows importing module metadata before FastAPI is installed in venv
    app = None

