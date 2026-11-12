"""Agent API domain ports for asynchronous LangGraph job management."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class AgentRunTicket:
    """Asynchronous ticket returned immediately (202 Accepted) when an Agent run is queued."""

    run_id: str
    trigger_mode: str
    symbol: str
    status: str
    queued_at: datetime


class AgentRunQueuePort(Protocol):
    """Port for persisting QUEUED agent runs in PostgreSQL and notifying agent-worker."""

    async def enqueue_run(
        self,
        symbol: str,
        prompt_summary: str,
        requested_by: str | None,
        trigger_mode: str = "ON_DEMAND",
    ) -> AgentRunTicket: ...

