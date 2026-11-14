"""Unified Microservices API Gateway Router & Service Mesh Dispatcher (`svc-api-gateway`, Port 8000)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.backend.runtime import PlatformRuntimeContainer


class InternalDispatchRequest(BaseModel):
    method: str = Field(default="GET")
    path: str = Field(..., description="Target path inside the microservice, e.g. /api/v1/health/live")
    params: dict[str, Any] | None = Field(default=None)
    json_body: dict[str, Any] | None = Field(default=None)


def build_microservices_gateway_router(runtime: PlatformRuntimeContainer) -> APIRouter:
    """Build `/api/v1/microservices` router exposing topology, health checks, and internal ASGI dispatch."""
    router = APIRouter()

    @router.get("/topology")
    async def get_microservices_topology() -> dict[str, Any]:
        """Return full microservice topology manifest with encrypted internal IP:Port bindings."""
        return runtime.microservice_registry.get_topology_manifest()

    @router.get("/health")
    async def check_all_microservices_health() -> dict[str, Any]:
        """Probe `/api/v1/health/live` across all registered standalone microservices."""
        results: dict[str, Any] = {}
        for service_id in (
            "svc-market-hot",
            "svc-historical-backfill",
            "svc-analytics-quant",
            "svc-catalog-governance",
            "svc-iam-security",
            "svc-intelligence-agent",
            "svc-data-plane-v01",
        ):
            res = await runtime.microservice_registry.dispatch_internal_request(
                service_id=service_id,
                method="GET",
                path="/api/v1/health/live",
            )
            results[service_id] = res["payload"]
        return {
            "gateway": "svc-api-gateway",
            "all_healthy": all(v.get("status") == "alive" for v in results.values()),
            "microservices": results,
        }

    @router.post("/dispatch/{service_id}")
    async def dispatch_to_microservice(
        service_id: str,
        req: InternalDispatchRequest,
    ) -> dict[str, Any]:
        """Route a request directly to an isolated microservice instance via `MicroserviceRegistry`."""
        try:
            return await runtime.microservice_registry.dispatch_internal_request(
                service_id=service_id,
                method=req.method,
                path=req.path,
                json_body=req.json_body,
                params=req.params,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return router

