---
doc_id: CAP-INT-ORC-UC-005
title: "Use Case UC-INT-005: Handle Invalid Symbol or Tool Execution Failure"
doc_type: specification
plane: intelligence-plane
scope_level: use-case
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - CAP-INT-ORC-REQ-001
  - CAP-INT-ORC-ERR-001
  - DIAG-INT-ORC-STATE-001
requirement_ids:
  - UC-INT-005
  - AC-INT-005
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented graceful Node 1 symbol rejection vs unhandled runtime failure gaps in Nodes 2-5."
---

# Use Case UC-INT-005: Handle Invalid Symbol or Tool Execution Failure

## 1. Identification, Actors & Trigger

- **Use Case ID**: `UC-INT-005`
- **Primary Actor**: `MarketIntelligenceGraph` / `ControlledToolGateway`.
- **Supporting Actors**: `ReportValidator`, `PlatformRuntimeContainer`.
- **Trigger**: Request supplies an unmonitored `symbol` (e.g., `DOGEFAKEUSDT`) OR a tool/validator exception occurs during execution.

## 2. Preconditions, Permissions & Input/Output

- **Preconditions**: Investigation state created and passed to `run_investigation(state)`.
- **Permissions**: Internal guardrail enforcement (runs prior to or during tool execution).
- **Inputs**: Invalid `symbol` or failing `tool_name` / `params` / `report`.
- **Outputs**:
  - **Node 1 Invalid Symbol (`AS-IS`)**: `AgentWorkflowState(status="FAILED", final_report={"error": ...})`.
  - **Nodes 2–5 Exception (`AS-IS` Gap)**: Unhandled exception propagates; no `FAILED` transition or report persistence.

## 3. Main, Alternative & Exception Flows

### 3.1 Main Flow — Invalid Symbol Rejection (`AS-IS` Implemented)

1. `intake_and_guardrail_node` normalizes `state.symbol = state.symbol.upper().strip()`.
2. Checks `state.symbol not in self._monitored_symbols`.
3. Transitions `state.status = "FAILED"`, sets `state.final_report = {"error": f"Symbol '{state.symbol}' is not in monitored catalog."}`, and returns `state` without calling planner or tools.

### 3.2 Alternative Flow — `TARGET` Graceful Tool/Timeout Handling

1. On `UnauthorizedToolAccessError`, `ToolQueryLimitExceededError`, `TimeoutError`, or `ReportProvenanceError`, Node 3/5 catches the exception, records a `TIMEOUT`/`VALIDATION_ERROR` audit record, transitions `state.status = "FAILED"`, persists failure metadata, and returns cleanly (`NOT_IMPLEMENTED AS-IS`).

### 3.3 Exception Flow — `AS-IS` Unhandled Failures in Nodes 2–5

- **E1 (Tool Gateway Rejection)**: `UnauthorizedToolAccessError` or `ToolQueryLimitExceededError` raised in Node 3 aborts `run_investigation()` without updating `state.status`, leaving `runtime.agent_runs[run_id].status == "RUNNING"` permanently.
- **E2 (Tool Timeout)**: `asyncio.TimeoutError` inside `ControlledToolGateway` aborts the workflow unhandled.
- **E3 (Empty Evidence or Bad Citation)**: `ReportProvenanceError` in Node 5 aborts unhandled without marking `FAILED`.

## 4. Business Rules, State Transitions, Tool Contracts & Acceptance Criteria

- **Business Rules**: `RULE-INT-001`, `RULE-INT-004`, `RULE-INT-006`.
- **State Transitions**: `QUEUED -> FAILED` (Node 1); `RUNNING -> FAILED` (`TARGET` only; unhandled crash `AS-IS`).
- **Relevant Tool Contracts**: `gateway_common_errors` in [tool-contracts.yaml](../../../../../shared-contracts/tool-contracts.yaml).
- **Acceptance Criteria (`AC-INT-005`)**: Submitting `"DOGEFAKEUSDT"` returns `state.status == "FAILED"`, `len(state.evidence_trail) == 0`, and `final_report["error"]` explains catalog rejection (`test_three_planes_framework.py:346-353`).
- **Related Diagrams**: [workflow-state-diagram.md](../workflows/workflow-state-diagram.md) (`DIAG-INT-ORC-STATE-001`), [tool-gateway-boundaries.md](../../../../../architecture/diagrams/tool-gateway-boundaries.md) (`DIAG-INT-GW-001`).
- **Open Questions**: Target exception-catching boundary inside `MarketIntelligenceGraph.run_investigation()` so failed runs never remain stuck in `RUNNING`.
