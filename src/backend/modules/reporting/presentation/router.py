"""Reporting Presentation Layer (Retrieval of Verified Structured Analysis Reports)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    from fastapi import APIRouter, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = Any  # type: ignore[misc,assignment]
    HTTPException = Exception  # type: ignore[misc,assignment]

if TYPE_CHECKING:
    from src.backend.runtime import PlatformRuntimeContainer


def build_reporting_router(runtime: PlatformRuntimeContainer) -> Any:
    """Build the FastAPI APIRouter for the Reporting domain."""
    router = APIRouter()

    @router.get("")
    async def list_reports(symbol: str | None = None) -> dict[str, Any]:
        items = []
        for rep in runtime.reports.values():
            if symbol is None or rep.symbol == symbol.upper():
                items.append(
                    {
                        "run_id": rep.run_id,
                        "symbol": rep.symbol,
                        "summary": rep.summary,
                        "data_quality_status": rep.data_quality_status,
                        "citation_count": len(rep.provenance_citations),
                    }
                )
        return {"data": items, "meta": {"count": len(items)}}

    @router.get("/{run_id}")
    async def get_report_by_run_id(run_id: str) -> dict[str, Any]:
        rep = runtime.reports.get(run_id)
        if rep is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "ERR_REPORT_NOT_FOUND",
                    "message": f"Report for run {run_id} not found",
                },
            )
        return {
            "data": {
                "run_id": rep.run_id,
                "symbol": rep.symbol,
                "summary": rep.summary,
                "quantitative_evidence": rep.quantitative_evidence,
                "anomalies_detected": list(rep.anomalies_detected),
                "data_quality_status": rep.data_quality_status,
                "provenance_citations": [
                    {
                        "invocation_id": c.invocation_id,
                        "tool_name": c.tool_name,
                        "source_store": c.source_store,
                        "symbol": c.symbol,
                        "window_start": c.window_start.isoformat(),
                        "window_end": c.window_end.isoformat(),
                        "row_count": c.row_count,
                    }
                    for c in rep.provenance_citations
                ],
                "limitations_disclaimer": rep.limitations_disclaimer,
            }
        }

    return router
