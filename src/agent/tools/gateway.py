"""Controlled Tool Gateway enforcing whitelist, permissions, query limits, and provenance."""

from __future__ import annotations

import asyncio
import math
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from src.agent.tools.contracts import (
    APPROVED_TOOL_POLICIES,
    ApprovedAgentTool,
    ToolExecutionEnvelope,
    ToolProvenanceMetadata,
)


class UnauthorizedToolAccessError(PermissionError):
    """Raised when an Agent or caller attempts to invoke an unauthorized or unwhitelisted tool."""


class ToolQueryLimitExceededError(ValueError):
    """Raised when a tool invocation requests more rows/periods than permitted."""


def compute_deterministic_log_returns(prices: list[float]) -> list[float]:
    """Deterministic Python calculation of log returns (never delegated to LLM math)."""
    if len(prices) < 2:
        return []
    returns: list[float] = []
    for idx in range(1, len(prices)):
        prev_p = prices[idx - 1]
        curr_p = prices[idx]
        if prev_p <= 0 or curr_p <= 0:
            raise ValueError("Prices must be strictly positive for log return calculation")
        returns.append(math.log(curr_p / prev_p))
    return returns


def compute_deterministic_realized_volatility(
    prices: list[float],
    periods_per_year: int = 365 * 24,
) -> float:
    """Deterministic calculation of annualized realized volatility from price series."""
    log_returns = compute_deterministic_log_returns(prices)
    if len(log_returns) < 2:
        return 0.0
    mean_ret = sum(log_returns) / len(log_returns)
    variance = sum((r - mean_ret) ** 2 for r in log_returns) / (len(log_returns) - 1)
    return math.sqrt(variance * periods_per_year)


class ControlledToolGateway:
    """Security and determinism firewall mediating all Agent tool invocations (ADR-006)."""

    def __init__(
        self,
        handlers: dict[ApprovedAgentTool, Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]]
        | None = None,
    ) -> None:
        self._handlers = dict(handlers or {})

    async def execute_tool(
        self,
        tool_name: str,
        params: dict[str, Any],
        granted_permissions: frozenset[str],
    ) -> ToolExecutionEnvelope:
        """Validate whitelist, RBAC, row bounds, and timeout before running deterministic handler."""
        try:
            approved_tool = ApprovedAgentTool(tool_name)
        except ValueError as exc:
            raise UnauthorizedToolAccessError(
                f"Tool '{tool_name}' is not in the approved Tool Gateway whitelist"
            ) from exc

        policy = APPROVED_TOOL_POLICIES[approved_tool]
        if policy.required_permission not in granted_permissions:
            raise UnauthorizedToolAccessError(
                f"Missing required permission '{policy.required_permission}' for tool '{tool_name}'"
            )

        requested_limit = int(params.get("limit") or params.get("lookback_periods") or 1)
        if requested_limit > policy.max_rows_or_periods:
            raise ToolQueryLimitExceededError(
                f"Tool '{tool_name}' requested {requested_limit} rows/periods, "
                f"exceeding cap of {policy.max_rows_or_periods}"
            )

        now_utc = datetime.now(UTC)
        symbol = str(params.get("symbol", "MULTI")).upper()
        invocation_id = str(uuid.uuid4())

        handler = self._handlers.get(approved_tool)
        if handler is None:
            result_data: dict[str, Any] = {"status": "stub_ok", "tool": approved_tool.value}
        else:
            result_data = await asyncio.wait_for(handler(params), timeout=policy.timeout_seconds)

        provenance = ToolProvenanceMetadata(
            invocation_id=invocation_id,
            tool_name=approved_tool,
            source_store=policy.backing_store,
            symbol=symbol,
            window_start=params.get("start_time", now_utc),
            window_end=params.get("end_time", now_utc),
            row_count=int(result_data.get("row_count", 1)),
            executed_at=now_utc,
        )
        return ToolExecutionEnvelope(
            status="SUCCESS",
            data=result_data,
            provenance=provenance,
        )

