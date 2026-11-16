"""Real-Time Data Platform Observability REST, SSE, and WebSocket API Gateway.

Strictly preserves Clean Architecture boundaries (`TC-006`) by importing no lower data-plane
packages directly and delegating all reads/probes through `PlatformRuntimeContainer`.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer


class LiveProbeRequest(BaseModel):
    symbol: str = Field(default="BTCUSDT", min_length=3, max_length=20)
    interval: str = Field(default="1m", pattern="^(1m|5m|15m|1h|4h|1d)$")
    limit: int = Field(default=10, ge=1, le=50)
    fetch_binance: bool = False


class DemoSimulationRequest(BaseModel):
    action: str = Field(
        default="emit_batch",
        pattern="^(emit_batch|inject_dlq|flush_lakehouse|run_full_pipeline)$",
    )
    symbol: str = Field(default="BTCUSDT", min_length=3, max_length=20)
    count: int = Field(default=5, ge=1, le=25)


def build_observability_router(runtime: PlatformRuntimeContainer) -> APIRouter:
    """Build non-mutating telemetry REST + SSE routes under `/api/v1/observability`."""
    router = APIRouter()

    @router.get("/overview")
    async def get_observability_overview(
        window: str = Query(default="all", pattern="^(1m|5m|15m|1h|24h|all)$"),
        provider: str | None = Query(default=None),
        symbol: str | None = Query(default=None),
        mode: str | None = Query(default=None),
        force_probe: bool = Query(default=False),
    ) -> dict[str, Any]:
        runtime.observability_metrics.record_serving_request("observability_overview", "2xx")
        return await runtime.get_observability_overview(
            window=window,
            provider=provider,
            symbol=symbol,
            mode=mode,
            force_probe=force_probe,
        )

    @router.get("/topology")
    async def get_observability_topology(
        window: str = Query(default="all", pattern="^(1m|5m|15m|1h|24h|all)$"),
        provider: str | None = Query(default=None),
        symbol: str | None = Query(default=None),
        mode: str | None = Query(default=None),
    ) -> dict[str, Any]:
        runtime.observability_metrics.record_serving_request("observability_topology", "2xx")
        return await runtime.get_observability_topology(
            window=window,
            provider=provider,
            symbol=symbol,
            mode=mode,
        )

    @router.get("/kafka")
    async def get_observability_kafka(
        topic: str | None = Query(default=None),
        window: str = Query(default="5m", pattern="^(1m|5m|15m|1h|24h|all)$"),
    ) -> dict[str, Any]:
        runtime.observability_metrics.record_serving_request("observability_kafka", "2xx")
        return runtime.get_observability_kafka(selected_topic=topic, window=window)

    @router.get("/storage")
    async def get_observability_storage(
        dataset: str | None = Query(default=None),
    ) -> dict[str, Any]:
        runtime.observability_metrics.record_serving_request("observability_storage", "2xx")
        return runtime.get_observability_storage(dataset=dataset)

    @router.get("/latency")
    async def get_observability_latency(
        window: str = Query(default="all", pattern="^(1m|5m|15m|1h|24h|all)$"),
        provider: str | None = Query(default=None),
        symbol: str | None = Query(default=None),
        mode: str | None = Query(default=None),
        slow_threshold_ms: float = Query(default=25.0, ge=0.0, le=60000.0),
    ) -> dict[str, Any]:
        runtime.observability_metrics.record_serving_request("observability_latency", "2xx")
        return runtime.get_observability_latency(
            window=window,
            provider=provider,
            symbol=symbol,
            mode=mode,
            slow_threshold_ms=slow_threshold_ms,
        )

    @router.get("/traces")
    async def list_observability_traces(
        window: str = Query(default="all", pattern="^(1m|5m|15m|1h|24h|all)$"),
        mode: str | None = Query(default=None),
        provider: str | None = Query(default=None),
        symbol: str | None = Query(default=None),
        status: str | None = Query(default=None),
        topic: str | None = Query(default=None),
        slow_threshold_ms: float | None = Query(default=None, ge=0.0),
        only_errors: bool = Query(default=False),
        limit: int = Query(default=100, ge=1, le=500),
    ) -> dict[str, Any]:
        runtime.observability_metrics.record_serving_request("observability_traces", "2xx")
        items = runtime.get_observability_traces(
            window=window,
            mode=mode,
            provider=provider,
            symbol=symbol,
            status=status,
            topic=topic,
            slow_threshold_ms=slow_threshold_ms,
            only_errors=only_errors,
            limit=limit,
        )
        return {"count": len(items), "traces": items}

    @router.get("/traces/{event_id}")
    async def get_observability_trace_detail(event_id: str) -> dict[str, Any]:
        trace = runtime.get_observability_trace_detail(event_id)
        if trace is None:
            runtime.observability_metrics.record_serving_request("observability_trace_detail", "4xx")
            raise HTTPException(status_code=404, detail=f"Trace not found for event_id={event_id}")
        runtime.observability_metrics.record_serving_request("observability_trace_detail", "2xx")
        return trace

    @router.get("/candles")
    async def get_observability_candles(
        provider: str = Query(default="binance"),
        symbol: str = Query(default="BTCUSDT"),
        interval: str = Query(default="1m", pattern="^(1m|5m|15m|1h|4h|1d)$"),
        hours: int = Query(default=24, ge=1, le=168),
        limit: int = Query(default=200, ge=1, le=1000),
    ) -> dict[str, Any]:
        runtime.observability_metrics.record_serving_request("observability_candles", "2xx")
        return runtime.get_observability_candles(
            provider=provider,
            symbol=symbol,
            interval=interval,
            hours=hours,
            limit=limit,
        )

    @router.post("/live/probe")
    async def trigger_live_probe(req: LiveProbeRequest) -> dict[str, Any]:
        runtime.observability_metrics.record_serving_request("observability_live_probe", "2xx")
        infra = await runtime.probe_external_infrastructure(force=True)
        binance_result = None
        if req.fetch_binance:
            binance_result = await runtime.fetch_live_binance_market_data(
                symbol=req.symbol, interval=req.interval, limit=req.limit
            )
        return {"infrastructure": infra, "binance_live_pull": binance_result}

    @router.post("/demo/emit")
    async def trigger_demo_simulation(req: DemoSimulationRequest) -> dict[str, Any]:
        runtime.observability_metrics.record_serving_request("observability_demo_emit", "2xx")
        return await runtime.trigger_demo_action(
            action=req.action, symbol=req.symbol, count=req.count
        )

    @router.get("/stream")
    async def stream_observability_sse(
        request: Request,
        max_events: int | None = Query(default=None, ge=1, le=1000),
    ) -> StreamingResponse:
        """Real-time Server-Sent Events stream pushing live `EventLifecycleTrace` & periodic telemetry."""
        loop = asyncio.get_running_loop()
        sub_id, queue = runtime.trace_registry.subscribe(loop)

        async def event_generator() -> AsyncIterator[str]:
            sent = 0
            try:
                overview = await runtime.get_observability_overview()
                topology = await runtime.get_observability_topology()
                snapshot_payload = json.dumps(
                    {"type": "snapshot", "overview": overview, "topology": topology},
                    default=str,
                )
                yield f"event: snapshot\ndata: {snapshot_payload}\n\n"
                sent += 1
                if max_events is not None and sent >= max_events:
                    return

                while True:
                    if await request.is_disconnected():
                        break
                    try:
                        trace_item = await asyncio.wait_for(queue.get(), timeout=2.5)
                        msg = json.dumps({"type": "trace", "trace": trace_item}, default=str)
                        yield f"event: trace\ndata: {msg}\n\n"
                        sent += 1
                    except TimeoutError:
                        hb_overview = await runtime.get_observability_overview()
                        msg = json.dumps({"type": "heartbeat", "overview": hb_overview}, default=str)
                        yield f"event: heartbeat\ndata: {msg}\n\n"
                        sent += 1
                    if max_events is not None and sent >= max_events:
                        break
            finally:
                runtime.trace_registry.unsubscribe(sub_id)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return router


def build_observability_ws_router(runtime: PlatformRuntimeContainer) -> APIRouter:
    """Build WebSocket endpoint `/ws/v1/observability/stream` for bidirectional UI telemetry."""
    router = APIRouter()

    @router.websocket("/ws/v1/observability/stream")
    async def ws_observability_stream(websocket: WebSocket) -> None:
        await websocket.accept()
        loop = asyncio.get_running_loop()
        sub_id, queue = runtime.trace_registry.subscribe(loop)

        async def _send_loop() -> None:
            overview = await runtime.get_observability_overview()
            await websocket.send_json({"type": "snapshot", "overview": overview})
            while True:
                try:
                    trace_item = await asyncio.wait_for(queue.get(), timeout=3.0)
                    await websocket.send_json({"type": "trace", "trace": trace_item})
                except TimeoutError:
                    hb_overview = await runtime.get_observability_overview()
                    await websocket.send_json({"type": "heartbeat", "overview": hb_overview})

        async def _recv_loop() -> None:
            while True:
                raw_msg = await websocket.receive_text()
                with contextlib.suppress(Exception):
                    parsed = json.loads(raw_msg)
                    if isinstance(parsed, dict) and parsed.get("type") == "ping":
                        await websocket.send_json(
                            {"type": "pong", "timestamp": parsed.get("timestamp")}
                        )

        sender = asyncio.create_task(_send_loop())
        receiver = asyncio.create_task(_recv_loop())
        try:
            done, pending = await asyncio.wait(
                {sender, receiver}, return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
                with contextlib.suppress(BaseException):
                    await task
            for task in done:
                with contextlib.suppress(WebSocketDisconnect):
                    task.result()
        except WebSocketDisconnect:
            pass
        finally:
            with contextlib.suppress(Exception):
                runtime.trace_registry.unsubscribe(sub_id)

    return router
