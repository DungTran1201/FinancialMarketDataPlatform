"""Standalone Intelligence Agent & Reporting Microservice (`svc-intelligence-agent`, Port 8006)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI

if TYPE_CHECKING:
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer


def create_intelligence_microservice_app(runtime: PlatformRuntimeContainer | None = None) -> FastAPI:
    """Create standalone FastAPI application for `svc-intelligence-agent` (port 8006)."""
    from src.serving.api.modules.agent_api.presentation.router import build_agent_api_router
    from src.serving.api.modules.reporting.presentation.router import build_reporting_router
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer

    rt = runtime or PlatformRuntimeContainer()
    app = FastAPI(title="Intelligence Agent Microservice (svc-intelligence-agent)", version="0.1.0")
    app.state.runtime = rt

    @app.get("/api/v1/health/live")
    async def health_live() -> dict[str, Any]:
        return {
            "status": "alive",
            "service_id": "svc-intelligence-agent",
            "bounded_contexts": ["agent_api", "reporting"],
            "timestamp": datetime.now(UTC).isoformat(),
        }

    app.include_router(
        build_agent_api_router(runtime=rt),
        prefix="/api/v1/agents",
        tags=["Intelligence Plane (Agent Runs & SSE)"],
    )
    app.include_router(
        build_reporting_router(runtime=rt),
        prefix="/api/v1/reports",
        tags=["Intelligence Plane (Verified Reports)"],
    )
    return app
