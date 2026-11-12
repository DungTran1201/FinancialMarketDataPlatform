"""Contracts and Specifications for the 10 Mandatory Read-Only Deterministic Agent Tools."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


class ApprovedAgentTool(StrEnum):
    """Strict whitelist of the 10 approved deterministic Agent tools (Section 8.3)."""

    GET_LATEST_PRICE = "get_latest_price"
    GET_MARKET_SNAPSHOT = "get_market_snapshot"
    GET_HISTORICAL_CANDLES = "get_historical_candles"
    GET_MARKET_STATISTICS = "get_market_statistics"
    CALCULATE_RETURNS = "calculate_returns"
    CALCULATE_VOLATILITY = "calculate_volatility"
    CALCULATE_CORRELATION = "calculate_correlation"
    DETECT_ANOMALIES = "detect_anomalies"
    GET_DATA_FRESHNESS = "get_data_freshness"
    GENERATE_ANALYSIS_REPORT = "generate_analysis_report"


@dataclass(frozen=True, slots=True)
class ToolGovernancePolicy:
    """Defines timeout, row limits, required permission, and backing store for a tool."""

    tool: ApprovedAgentTool
    required_permission: str
    backing_store: str
    max_rows_or_periods: int
    timeout_seconds: float
    is_read_only_market_data: bool = True


APPROVED_TOOL_POLICIES: dict[ApprovedAgentTool, ToolGovernancePolicy] = {
    ApprovedAgentTool.GET_LATEST_PRICE: ToolGovernancePolicy(
        tool=ApprovedAgentTool.GET_LATEST_PRICE,
        required_permission="market:read",
        backing_store="redis_with_clickhouse_fallback",
        max_rows_or_periods=1,
        timeout_seconds=1.5,
    ),
    ApprovedAgentTool.GET_MARKET_SNAPSHOT: ToolGovernancePolicy(
        tool=ApprovedAgentTool.GET_MARKET_SNAPSHOT,
        required_permission="market:read",
        backing_store="redis_with_clickhouse_fallback",
        max_rows_or_periods=1,
        timeout_seconds=2.0,
    ),
    ApprovedAgentTool.GET_HISTORICAL_CANDLES: ToolGovernancePolicy(
        tool=ApprovedAgentTool.GET_HISTORICAL_CANDLES,
        required_permission="historical:read",
        backing_store="clickhouse_agent_ro",
        max_rows_or_periods=500,
        timeout_seconds=5.0,
    ),
    ApprovedAgentTool.GET_MARKET_STATISTICS: ToolGovernancePolicy(
        tool=ApprovedAgentTool.GET_MARKET_STATISTICS,
        required_permission="analytics:read",
        backing_store="clickhouse_mv_agent_ro",
        max_rows_or_periods=1,
        timeout_seconds=5.0,
    ),
    ApprovedAgentTool.CALCULATE_RETURNS: ToolGovernancePolicy(
        tool=ApprovedAgentTool.CALCULATE_RETURNS,
        required_permission="analytics:read",
        backing_store="clickhouse_agent_ro_deterministic_math",
        max_rows_or_periods=720,
        timeout_seconds=5.0,
    ),
    ApprovedAgentTool.CALCULATE_VOLATILITY: ToolGovernancePolicy(
        tool=ApprovedAgentTool.CALCULATE_VOLATILITY,
        required_permission="analytics:read",
        backing_store="clickhouse_agent_ro_deterministic_math",
        max_rows_or_periods=720,
        timeout_seconds=5.0,
    ),
    ApprovedAgentTool.CALCULATE_CORRELATION: ToolGovernancePolicy(
        tool=ApprovedAgentTool.CALCULATE_CORRELATION,
        required_permission="analytics:read",
        backing_store="clickhouse_agent_ro_deterministic_math",
        max_rows_or_periods=2160,
        timeout_seconds=8.0,
    ),
    ApprovedAgentTool.DETECT_ANOMALIES: ToolGovernancePolicy(
        tool=ApprovedAgentTool.DETECT_ANOMALIES,
        required_permission="analytics:read",
        backing_store="clickhouse_agent_ro_deterministic_math",
        max_rows_or_periods=168,
        timeout_seconds=5.0,
    ),
    ApprovedAgentTool.GET_DATA_FRESHNESS: ToolGovernancePolicy(
        tool=ApprovedAgentTool.GET_DATA_FRESHNESS,
        required_permission="market:read",
        backing_store="redis_and_clickhouse_metadata",
        max_rows_or_periods=1,
        timeout_seconds=3.0,
    ),
    ApprovedAgentTool.GENERATE_ANALYSIS_REPORT: ToolGovernancePolicy(
        tool=ApprovedAgentTool.GENERATE_ANALYSIS_REPORT,
        required_permission="agent:trigger",
        backing_store="postgres_agent_rw",
        max_rows_or_periods=1,
        timeout_seconds=3.0,
    ),
}


@dataclass(frozen=True, slots=True)
class ToolProvenanceMetadata:
    """Mandatory data provenance attached to every deterministic tool output."""

    invocation_id: str
    tool_name: ApprovedAgentTool
    source_store: str
    symbol: str
    window_start: datetime
    window_end: datetime
    row_count: int
    executed_at: datetime


@dataclass(frozen=True, slots=True)
class ToolExecutionEnvelope:
    """Standardized output wrapper returned by the Controlled Tool Gateway."""

    status: str  # SUCCESS | TIMEOUT | VALIDATION_ERROR | PERMISSION_DENIED
    data: dict[str, Any]
    provenance: ToolProvenanceMetadata

