"""FastAPI Modular Monolith Application Entrypoint, Defense-in-Depth Gateway & Health Checks (Plane B)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from src.backend.modules.iam.domain.security import IPAndEndpointCipher, RateLimitTier
from src.shared.config import PlatformConfig

if TYPE_CHECKING:
    from src.backend.runtime import PlatformRuntimeContainer


def get_liveness_status() -> dict[str, Any]:
    """Minimal liveness probe payload (verifies process responsiveness)."""
    config = PlatformConfig()
    return {
        "status": "alive",
        "service": "backend-api",
        "domain_origin": f"https://api.{config.platform_domain}",
        "environment": config.app_env,
        "timestamp": datetime.now(UTC).isoformat(),
    }


def get_readiness_status() -> dict[str, Any]:
    """Readiness probe reporting encrypted/masked service bindings (never leaks raw IP:Port)."""
    config = PlatformConfig()
    cipher = IPAndEndpointCipher(config.jwt_secret_key)
    kafka_host, _, kafka_port_str = config.kafka_bootstrap_servers.partition(":")
    kafka_port = int(kafka_port_str or "9092")
    return {
        "status": "ready",
        "service": "backend-api",
        "domain_origin": f"https://api.{config.platform_domain}",
        "dependencies": {
            "redis": cipher.mask_service_endpoint("redis", config.redis_host, config.redis_port),
            "clickhouse": cipher.mask_service_endpoint(
                "clickhouse", config.clickhouse_host, config.clickhouse_http_port
            ),
            "postgres": cipher.mask_service_endpoint("postgres", config.postgres_host, config.postgres_port),
            "kafka": cipher.mask_service_endpoint("kafka", kafka_host, kafka_port),
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }


def create_app(
    config: PlatformConfig | None = None,
    tier_overrides: dict[RateLimitTier, int] | None = None,
    runtime: PlatformRuntimeContainer | None = None,
) -> Any:
    """Create the FastAPI Modular Monolith application wiring all 8 domain modules across Planes A, B, C."""
    from fastapi import FastAPI

    from src.backend.modules.agent_api.presentation.router import build_agent_api_router
    from src.backend.modules.analytics.presentation.router import build_analytics_router
    from src.backend.modules.catalog.presentation.router import build_catalog_router
    from src.backend.modules.historical.presentation.router import build_historical_router
    from src.backend.modules.iam.presentation.router import (
        build_iam_security_router,
        install_security_defense_middleware,
    )
    from src.backend.modules.market.presentation.router import build_market_router
    from src.backend.modules.platform_config.presentation.router import (
        build_platform_config_router,
    )
    from src.backend.modules.reporting.presentation.router import build_reporting_router
    from src.backend.runtime import PlatformRuntimeContainer

    cfg = config or PlatformConfig()
    rt = runtime or PlatformRuntimeContainer(config=cfg)
    app = FastAPI(
        title="Real-time Financial Market Data Platform API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    app.state.runtime = rt

    jwt_service, ip_cipher, _ = install_security_defense_middleware(app, config=cfg, tier_overrides=tier_overrides)

    @app.get("/api/v1/health/live", tags=["Health"])
    async def health_live() -> dict[str, Any]:
        return get_liveness_status()

    @app.get("/api/v1/health/ready", tags=["Health"])
    async def health_ready() -> dict[str, Any]:
        return get_readiness_status()

    app.include_router(
        build_iam_security_router(jwt_service=jwt_service, ip_cipher=ip_cipher, config=cfg),
        prefix="/api/v1/auth",
        tags=["IAM & Security"],
    )
    app.include_router(
        build_market_router(runtime=rt),
        prefix="/api/v1/market",
        tags=["Market (Hot Path + OLAP Fallback)"],
    )
    app.include_router(
        build_historical_router(runtime=rt),
        prefix="/api/v1/historical",
        tags=["Historical OHLCV, Trades & Backfills"],
    )
    app.include_router(
        build_analytics_router(runtime=rt),
        prefix="/api/v1/analytics",
        tags=["Analytics, Correlations & Anomalies"],
    )
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


try:
    app = create_app()
except ModuleNotFoundError:  # Allows importing module metadata before FastAPI is installed in venv
    app = None
