"""Standalone IAM & Security Defense Microservice (`svc-iam-security`, Port 8005)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI

from src.backend.modules.iam.presentation.router import (
    build_iam_security_router,
    install_security_defense_middleware,
)
from src.shared.config import PlatformConfig


def create_iam_microservice_app(config: PlatformConfig | None = None) -> FastAPI:
    """Create standalone FastAPI application for `svc-iam-security` (port 8005)."""
    cfg = config or PlatformConfig()
    app = FastAPI(title="IAM & Security Microservice (svc-iam-security)", version="0.1.0")
    jwt_service, ip_cipher, _ = install_security_defense_middleware(app, config=cfg)

    @app.get("/api/v1/health/live")
    async def health_live() -> dict[str, Any]:
        return {
            "status": "alive",
            "service_id": "svc-iam-security",
            "bounded_context": "iam",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    app.include_router(
        build_iam_security_router(jwt_service=jwt_service, ip_cipher=ip_cipher, config=cfg),
        prefix="/api/v1/auth",
        tags=["IAM & Security"],
    )
    return app

