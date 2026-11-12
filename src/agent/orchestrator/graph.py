"""Stateful LangGraph Workflow Orchestrator Blueprint (MarketIntelligenceGraph)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.agent.tools.contracts import ToolExecutionEnvelope

WORKFLOW_NODES: tuple[str, ...] = (
    "intake_and_guardrail_node",
    "investigation_planner_node",
    "tool_gateway_executor_node",
    "evidence_verifier_node",
    "report_synthesizer_node",
)


@dataclass(slots=True)
class AgentWorkflowState:
    """Explicit state schema persisted across LangGraph nodes in PostgreSQL."""

    run_id: str
    trigger_mode: str  # ON_DEMAND | EVENT_TRIGGERED
    symbol: str
    prompt_summary: str
    max_iterations: int = 6
    token_budget: int = 8000
    current_iteration: int = 0
    tokens_consumed: int = 0
    planned_tools: list[dict[str, Any]] = field(default_factory=list)
    evidence_trail: list[ToolExecutionEnvelope] = field(default_factory=list)
    final_report: dict[str, Any] | None = None
    status: str = "QUEUED"

    def can_continue_planning(self) -> bool:
        """Enforce bounded iteration and token budget constraints (Section 8.4)."""
        return (
            self.current_iteration < self.max_iterations
            and self.tokens_consumed < int(self.token_budget * 0.8)
            and self.status == "RUNNING"
        )

