"""Deterministic LangGraph-Compatible Market Intelligence Orchestrator (`COMP-007`)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.intelligence.reporting.validator import ReportValidator
from src.intelligence.tools.contracts import ApprovedAgentTool
from src.intelligence.tools.gateway import ControlledToolGateway
from src.intelligence.workflows.investigation import AgentWorkflowState


class DeterministicMockLLMAdapter:
    """MOCKED External LLM Narrative Adapter (`LLM_PROVIDER=mock` in `.env`).

    Important: This adapter NEVER performs quantitative math or direct database access.
    All numbers come from `ControlledToolGateway` deterministic tools; this adapter only
    formats the narrative summary and accounts for token budget usage when offline.
    """

    def plan_tool_sequence(self, state: AgentWorkflowState) -> tuple[list[dict[str, Any]], int]:
        if state.current_iteration == 0:
            tools = [
                {
                    "tool": ApprovedAgentTool.GET_LATEST_PRICE.value,
                    "params": {"symbol": state.symbol},
                },
                {
                    "tool": ApprovedAgentTool.GET_MARKET_SNAPSHOT.value,
                    "params": {"symbol": state.symbol},
                },
                {
                    "tool": ApprovedAgentTool.GET_HISTORICAL_CANDLES.value,
                    "params": {"symbol": state.symbol, "interval": "1m", "limit": 60},
                },
                {
                    "tool": ApprovedAgentTool.CALCULATE_RETURNS.value,
                    "params": {"symbol": state.symbol, "lookback_periods": 30},
                },
                {
                    "tool": ApprovedAgentTool.CALCULATE_VOLATILITY.value,
                    "params": {"symbol": state.symbol, "lookback_periods": 30},
                },
                {
                    "tool": ApprovedAgentTool.DETECT_ANOMALIES.value,
                    "params": {"symbol": state.symbol, "lookback_periods": 24},
                },
                {
                    "tool": ApprovedAgentTool.GET_DATA_FRESHNESS.value,
                    "params": {"symbol": state.symbol},
                },
            ]
            return tools, 420
        return [], 110

    def synthesize_narrative(self, state: AgentWorkflowState) -> tuple[dict[str, Any], int]:
        quant_evidence: dict[str, Any] = {}
        citations: list[dict[str, Any]] = []
        anomalies: list[str] = []

        for env in state.evidence_trail:
            tname = env.provenance.tool_name.value
            quant_evidence[tname] = env.data
            if tname == ApprovedAgentTool.DETECT_ANOMALIES.value and env.data.get("anomaly_detected"):
                anomalies.append(f"Z-score breach ({env.data.get('z_score')}) on {state.symbol}")
            citations.append(
                {
                    "invocation_id": env.provenance.invocation_id,
                    "tool_name": tname,
                    "source_store": env.provenance.source_store,
                    "symbol": env.provenance.symbol,
                    "window_start": env.provenance.window_start.isoformat(),
                    "window_end": env.provenance.window_end.isoformat(),
                    "row_count": env.provenance.row_count,
                }
            )

        report = {
            "run_id": state.run_id,
            "symbol": state.symbol,
            "trigger_mode": state.trigger_mode,
            "summary": (
                f"Deterministic market intelligence report for {state.symbol} "
                f"({len(citations)} verified tool executions)."
            ),
            "quantitative_evidence": quant_evidence,
            "anomalies_detected": anomalies,
            "data_quality_status": "HEALTHY",
            "provenance_citations": citations,
            "limitations_disclaimer": (
                "Generated via ControlledToolGateway deterministic tools; LLM narrative adapter=mock."
            ),
            "completed_at": datetime.now(UTC).isoformat(),
        }
        return report, 540


class MarketIntelligenceGraph:
    """Executes the 5-node stateful investigation workflow in isolated Plane C (`ADR-006`)."""

    def __init__(
        self,
        tool_gateway: ControlledToolGateway,
        llm_adapter: DeterministicMockLLMAdapter | None = None,
        monitored_symbols: tuple[str, ...] = (
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
            "BNBUSDT",
            "XRPUSDT",
        ),
    ) -> None:
        self._gateway = tool_gateway
        self._llm = llm_adapter or DeterministicMockLLMAdapter()
        self._monitored_symbols = {s.upper() for s in monitored_symbols}
        self._agent_permissions = frozenset({"market:read", "historical:read", "analytics:read", "agent:trigger"})

    async def run_investigation(self, state: AgentWorkflowState) -> AgentWorkflowState:
        """Execute Nodes 1 -> 2 -> 3 -> 4 -> 5 deterministically with provenance validation."""
        # Node 1: intake_and_guardrail_node
        state.visited_nodes.append("intake_and_guardrail_node")
        state.symbol = state.symbol.upper().strip()
        if state.symbol not in self._monitored_symbols:
            state.status = "FAILED"
            state.final_report = {"error": f"Symbol '{state.symbol}' is not in monitored catalog."}
            return state
        state.status = "RUNNING"

        # Loop Nodes 2 -> 3 -> 4 bounded by `can_continue_planning()`
        while state.can_continue_planning():
            # Node 2: investigation_planner_node
            state.visited_nodes.append("investigation_planner_node")
            planned, plan_tokens = self._llm.plan_tool_sequence(state)
            state.tokens_consumed += plan_tokens
            state.planned_tools = planned
            state.current_iteration += 1

            if not state.planned_tools:
                break

            # Node 3: tool_gateway_executor_node
            state.visited_nodes.append("tool_gateway_executor_node")
            for item in state.planned_tools:
                envelope = await self._gateway.execute_tool(
                    tool_name=str(item["tool"]),
                    params=dict(item.get("params", {})),
                    granted_permissions=self._agent_permissions,
                )
                state.evidence_trail.append(envelope)

            # Node 4: evidence_verifier_node
            state.visited_nodes.append("evidence_verifier_node")
            if len(state.evidence_trail) >= 3:
                break

        # Node 5: report_synthesizer_node
        state.visited_nodes.append("report_synthesizer_node")
        report, synth_tokens = self._llm.synthesize_narrative(state)
        state.tokens_consumed += synth_tokens
        ReportValidator.validate_report(report, state.evidence_trail)

        # Persist report via Tool #10 (`generate_analysis_report`)
        persist_env = await self._gateway.execute_tool(
            tool_name=ApprovedAgentTool.GENERATE_ANALYSIS_REPORT.value,
            params={"symbol": state.symbol, "report": report},
            granted_permissions=self._agent_permissions,
        )
        state.evidence_trail.append(persist_env)
        state.final_report = report
        state.status = "COMPLETED"
        return state
