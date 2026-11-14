"""Microservice Registry, Service Discovery & Inter-Service ASGI Dispatch Engine (`ADR-007`)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx
from fastapi import FastAPI

from src.backend.modules.iam.domain.security import IPAndEndpointCipher
from src.shared.config import PlatformConfig


@dataclass(frozen=True, slots=True)
class MicroserviceDescriptor:
    """Metadata descriptor for an independently deployable microservice."""

    service_id: str
    service_name: str
    plane: str  # Plane A (Data) | Plane B (Application) | Plane C (Intelligence)
    bounded_contexts: tuple[str, ...]
    internal_host: str
    internal_port: int
    route_prefixes: tuple[str, ...]
    backing_stores: tuple[str, ...]
    sla_p95_ms: int


CANONICAL_MICROSERVICES: tuple[MicroserviceDescriptor, ...] = (
    MicroserviceDescriptor(
        service_id="svc-api-gateway",
        service_name="Unified HTTPS API Gateway & WAF Router",
        plane="Plane B (Application & Edge Gateway)",
        bounded_contexts=("gateway", "waf", "rate_limiter"),
        internal_host="svc-api-gateway.fmdp.internal",
        internal_port=8000,
        route_prefixes=("/api/v1/health", "/api/v1/microservices"),
        backing_stores=("redis_rate_limiter",),
        sla_p95_ms=25,
    ),
    MicroserviceDescriptor(
        service_id="svc-market-hot",
        service_name="Real-Time Market Hot-State & WebSocket Service",
        plane="Plane B (Application Serving)",
        bounded_contexts=("market",),
        internal_host="svc-market-hot.fmdp.internal",
        internal_port=8001,
        route_prefixes=("/api/v1/market", "/ws/v1/market"),
        backing_stores=("redis_hot_cache", "clickhouse_fallback"),
        sla_p95_ms=50,
    ),
    MicroserviceDescriptor(
        service_id="svc-historical-backfill",
        service_name="Historical OLAP Query & Backfill Control Service",
        plane="Plane B (Application Serving)",
        bounded_contexts=("historical",),
        internal_host="svc-historical-backfill.fmdp.internal",
        internal_port=8002,
        route_prefixes=("/api/v1/historical",),
        backing_stores=("clickhouse_olap", "postgresql_watermarks"),
        sla_p95_ms=500,
    ),
    MicroserviceDescriptor(
        service_id="svc-analytics-quant",
        service_name="Quantitative Analytics, Correlation & Anomaly Service",
        plane="Plane B (Application Serving)",
        bounded_contexts=("analytics",),
        internal_host="svc-analytics-quant.fmdp.internal",
        internal_port=8003,
        route_prefixes=("/api/v1/analytics",),
        backing_stores=("clickhouse_mv", "redis_cache"),
        sla_p95_ms=400,
    ),
    MicroserviceDescriptor(
        service_id="svc-catalog-governance",
        service_name="Data Catalog, Freshness SLI & Platform Config Service",
        plane="Plane B (Application & Control)",
        bounded_contexts=("catalog", "platform_config"),
        internal_host="svc-catalog-governance.fmdp.internal",
        internal_port=8004,
        route_prefixes=("/api/v1/catalog", "/api/v1/platform"),
        backing_stores=("postgresql_metadata", "minio_iceberg_lakehouse"),
        sla_p95_ms=150,
    ),
    MicroserviceDescriptor(
        service_id="svc-iam-security",
        service_name="IAM Authentication, JWT HS256 & Endpoint Cipher Service",
        plane="Plane B (Security & Identity)",
        bounded_contexts=("iam",),
        internal_host="svc-iam-security.fmdp.internal",
        internal_port=8005,
        route_prefixes=("/api/v1/auth",),
        backing_stores=("postgresql_iam", "redis_revocation_list"),
        sla_p95_ms=80,
    ),
    MicroserviceDescriptor(
        service_id="svc-intelligence-agent",
        service_name="Agentic Intelligence Orchestrator & Verified Reporting Service",
        plane="Plane C (Intelligence Plane)",
        bounded_contexts=("agent_api", "reporting"),
        internal_host="svc-intelligence-agent.fmdp.internal",
        internal_port=8006,
        route_prefixes=("/api/v1/agents", "/api/v1/reports"),
        backing_stores=("controlled_tool_gateway", "postgresql_reports"),
        sla_p95_ms=2500,
    ),
    MicroserviceDescriptor(
        service_id="svc-data-plane-v01",
        service_name="End-to-End Data Platform v0.1 Pipeline, Gold Marts & Lineage Service",
        plane="Plane A (Data Plane)",
        bounded_contexts=("collectors", "kafka_streaming", "medallion_lakehouse", "quality_lineage"),
        internal_host="svc-data-plane-v01.fmdp.internal",
        internal_port=8007,
        route_prefixes=("/api/v1/data-platform/v01",),
        backing_stores=("kafka", "redis", "clickhouse", "minio_iceberg_bronze_silver_gold"),
        sla_p95_ms=1000,
    ),
)


class MicroserviceRegistry:
    """Service discovery registry managing standalone ASGI microservice instances and encrypted endpoints."""

    def __init__(self, config: PlatformConfig | None = None) -> None:
        self.config = config or PlatformConfig()
        self.cipher = IPAndEndpointCipher(self.config.jwt_secret_key)
        self._descriptors: dict[str, MicroserviceDescriptor] = {
            d.service_id: d for d in CANONICAL_MICROSERVICES
        }
        self._asgi_apps: dict[str, FastAPI] = {}

    def register_asgi_app(self, service_id: str, app: FastAPI) -> None:
        self._asgi_apps[service_id] = app

    def get_asgi_app(self, service_id: str) -> FastAPI | None:
        return self._asgi_apps.get(service_id)

    def get_topology_manifest(self) -> dict[str, Any]:
        """Return microservice architecture topology with encrypted internal IP:Port bindings."""
        services_list = []
        for desc in CANONICAL_MICROSERVICES:
            masked = self.cipher.mask_service_endpoint(
                desc.service_id, desc.internal_host, desc.internal_port
            )
            services_list.append(
                {
                    "service_id": desc.service_id,
                    "service_name": desc.service_name,
                    "plane": desc.plane,
                    "bounded_contexts": list(desc.bounded_contexts),
                    "route_prefixes": list(desc.route_prefixes),
                    "backing_stores": list(desc.backing_stores),
                    "sla_p95_ms": desc.sla_p95_ms,
                    "encrypted_binding": masked,
                    "status": "ONLINE" if desc.service_id in self._asgi_apps else "REGISTERED",
                }
            )
        return {
            "architecture_style": "domain_microservices_v01",
            "adr_reference": "ADR-007",
            "total_microservices": len(services_list),
            "services": services_list,
            "generated_at": datetime.now(UTC).isoformat(),
        }

    async def dispatch_internal_request(
        self,
        service_id: str,
        method: str,
        path: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Dispatch an internal request directly to an isolated microservice ASGI app via `httpx.ASGITransport`."""
        target_app = self._asgi_apps.get(service_id)
        if target_app is None:
            raise KeyError(f"Microservice '{service_id}' is not mounted in registry")
        transport = httpx.ASGITransport(app=target_app)
        async with httpx.AsyncClient(
            transport=transport, base_url=f"https://{service_id}.fmdp.local", timeout=10.0
        ) as client:
            resp = await client.request(method=method.upper(), url=path, json=json_body, params=params)
            return {
                "service_id": service_id,
                "status_code": resp.status_code,
                "payload": resp.json() if "application/json" in resp.headers.get("content-type", "") else resp.text,
            }

