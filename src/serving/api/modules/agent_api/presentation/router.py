"""Agent API Presentation Layer (`API-008`, `API-009` — Async LangGraph Runs & SSE)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

try:
    from fastapi import APIRouter, Body, Header, HTTPException
    from fastapi.responses import StreamingResponse
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = Any  # type: ignore[misc,assignment]
    Body = None  # type: ignore[assignment]
    Header = None  # type: ignore[assignment]
    HTTPException = Exception  # type: ignore[misc,assignment]
    StreamingResponse = Any  # type: ignore[misc,assignment]

if TYPE_CHECKING:
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer


def build_agent_api_router(runtime: PlatformRuntimeContainer) -> Any:
    """Build the FastAPI APIRouter for Plane C Agent Workflow Orchestration."""
    router = APIRouter()

    @router.post("/runs", status_code=202)
    async def create_agent_run(
        payload: dict[str, Any] = Body(...),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> dict[str, Any]:
        symbol = str(payload.get("symbol", "BTCUSDT")).upper()
        prompt_summary = str(
            payload.get("prompt_summary", f"Comprehensive market intelligence investigation for {symbol}")
        )
        trigger_mode = str(payload.get("trigger_mode", "ON_DEMAND")).upper()

        ticket, state = await runtime.execute_agent_investigation(
            symbol=symbol,
            prompt_summary=prompt_summary,
            trigger_mode=trigger_mode,
            idempotency_key=idempotency_key,
        )
        return {
            "data": {
                "run_id": ticket.run_id,
                "symbol": ticket.symbol,
                "trigger_mode": ticket.trigger_mode,
                "status": ticket.status,
                "queued_at": ticket.queued_at.isoformat(),
                "tool_calls_executed": len(state.evidence_trail),
            },
            "meta": {
                "execution_mode": "async_202_accepted",
                "plane": "Plane C (Intelligence Plane)",
            },
        }

    @router.get("/runs/{run_id}")
    async def get_agent_run_status(run_id: str) -> dict[str, Any]:
        state = runtime.agent_runs.get(run_id)
        if state is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "ERR_AGENT_RUN_NOT_FOUND",
                    "message": f"Agent run {run_id} not found",
                },
            )
        serialized_trail = [
            {
                "invocation_id": env.provenance.invocation_id,
                "tool_name": env.provenance.tool_name.value,
                "source_store": env.provenance.source_store,
                "symbol": env.provenance.symbol,
                "row_count": env.provenance.row_count,
                "status": env.status,
                "data": env.data,
            }
            for env in state.evidence_trail
        ]
        return {
            "data": {
                "run_id": state.run_id,
                "symbol": state.symbol,
                "trigger_mode": state.trigger_mode,
                "status": state.status,
                "visited_nodes": state.visited_nodes,
                "tokens_consumed": state.tokens_consumed,
                "evidence_trail": serialized_trail,
                "final_report": state.final_report,
            }
        }

    @router.get("/runs/{run_id}/events")
    async def stream_agent_run_events(run_id: str) -> Any:
        state = runtime.agent_runs.get(run_id)
        if state is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "ERR_AGENT_RUN_NOT_FOUND",
                    "message": f"Agent run {run_id} not found",
                },
            )

        async def _sse_generator() -> Any:
            for env in state.evidence_trail:
                step_payload = {
                    "invocation_id": env.provenance.invocation_id,
                    "tool_name": env.provenance.tool_name.value,
                    "source_store": env.provenance.source_store,
                    "symbol": env.provenance.symbol,
                    "status": env.status,
                }
                yield f"event: tool_invocation\ndata: {json.dumps(step_payload)}\n\n"
            final_event = {"run_id": state.run_id, "status": state.status}
            yield f"event: run_completed\ndata: {json.dumps(final_event)}\n\n"

        return StreamingResponse(_sse_generator(), media_type="text/event-stream")

    return router
