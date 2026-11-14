"""Platform Configuration Presentation Layer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    from fastapi import APIRouter
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = Any  # type: ignore[misc,assignment]

if TYPE_CHECKING:
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer


def build_platform_config_router(runtime: PlatformRuntimeContainer) -> Any:
    """Build the FastAPI APIRouter for Platform Configuration & Watermarks."""
    router = APIRouter()

    @router.get("/config")
    async def get_platform_configuration() -> dict[str, Any]:
        return {
            "data": {
                "app_env": runtime.config.app_env,
                "default_provider": runtime.config.default_provider,
                "market_staleness_threshold_ms": runtime.config.market_staleness_threshold_ms,
                "agent_max_iterations": runtime.config.agent_max_iterations,
                "agent_tool_timeout_seconds": runtime.config.agent_tool_timeout_seconds,
                "agent_max_tokens_per_run": runtime.config.agent_max_tokens_per_run,
                "active_symbols": list(runtime.monitored_instruments.keys()),
                "watermarks": {k: v.isoformat() for k, v in runtime.ingestion_watermarks.items()},
            }
        }

    return router
