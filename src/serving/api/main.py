"""FastAPI Modular Monolith Application Entrypoint, Defense-in-Depth Gateway & Health Checks (Plane B)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from src.shared.config.settings import PlatformConfig
from src.shared.security.primitives import IPAndEndpointCipher, RateLimitTier

if TYPE_CHECKING:
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer


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
    from fastapi.responses import PlainTextResponse

    from src.serving.api.gateway.service import build_microservices_gateway_router
    from src.serving.api.modules.agent_api.presentation.router import build_agent_api_router
    from src.serving.api.modules.analytics.presentation.router import build_analytics_router
    from src.serving.api.modules.catalog.presentation.router import build_catalog_router
    from src.serving.api.modules.historical.presentation.router import build_historical_router
    from src.serving.api.modules.iam.presentation.router import (
        build_iam_security_router,
        install_security_defense_middleware,
    )
    from src.serving.api.modules.market.presentation.router import build_market_router
    from src.serving.api.modules.platform_config.presentation.router import (
        build_platform_config_router,
    )
    from src.serving.api.modules.reporting.presentation.router import build_reporting_router
    from src.serving.api.services.data_plane import build_data_platform_v01_router
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer

    cfg = config or PlatformConfig()
    rt = runtime or PlatformRuntimeContainer(config=cfg)

    @asynccontextmanager
    async def lifespan(_app: Any) -> AsyncIterator[None]:
        try:
            yield
        finally:
            rt.close()

    app = FastAPI(
        title="Real-time Financial Market Data Platform API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.state.runtime = rt
    rt.microservice_registry.register_asgi_app("svc-api-gateway", app)

    jwt_service, ip_cipher, _ = install_security_defense_middleware(app, config=cfg, tier_overrides=tier_overrides)

    @app.get("/", tags=["Health"])
    async def root_service_index() -> dict[str, Any]:
        return {
            "service": "Real-time Financial Market Data Platform API",
            "version": "0.1.0",
            "status": "alive",
            "environment": cfg.app_env,
            "endpoints": {
                "swagger_docs": "/api/docs",
                "openapi_schema": "/api/openapi.json",
                "health_live": "/api/v1/health/live",
                "health_ready": "/api/v1/health/ready",
                "metrics": "/metrics",
                "observability_overview": "/api/v1/observability/overview",
                "observability_sse": "/api/v1/observability/stream",
                "observability_ws": "/ws/v1/observability/stream",
            },
            "timestamp": datetime.now(UTC).isoformat(),
        }

    @app.get("/api/v1/health/live", tags=["Health"])
    async def health_live() -> dict[str, Any]:
        return get_liveness_status()

    @app.get("/api/v1/health/ready", tags=["Health"])
    async def health_ready() -> dict[str, Any]:
        return get_readiness_status()

    @app.get(
        "/metrics",
        response_class=PlainTextResponse,
        response_model=None,
        tags=["Observability"],
    )
    async def root_prometheus_metrics() -> Any:
        return PlainTextResponse(content=rt.data_platform_v01.observability.export_prometheus_text())

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
    app.include_router(
        build_data_platform_v01_router(runtime=rt),
        prefix="/api/v1/data-platform/v01",
        tags=["Data Platform v0.1 (End-to-End 12 Stages)"],
    )
    app.include_router(
        build_microservices_gateway_router(runtime=rt),
        prefix="/api/v1/microservices",
        tags=["Microservices Gateway & Service Topology (ADR-007)"],
    )
    from src.serving.api.gateway.observability import (
        build_observability_router,
        build_observability_ws_router,
    )

    app.include_router(
        build_observability_router(runtime=rt),
        prefix="/api/v1/observability",
        tags=["Real-Time Data Platform Observatory Telemetry (FEAT-001)"],
    )
    app.include_router(
        build_observability_ws_router(runtime=rt),
        tags=["Real-Time Data Platform Observatory WebSocket (FEAT-001)"],
    )
    return app


try:
    app = create_app()
except ModuleNotFoundError:  # Allows importing module metadata before FastAPI is installed in venv
    app = None
