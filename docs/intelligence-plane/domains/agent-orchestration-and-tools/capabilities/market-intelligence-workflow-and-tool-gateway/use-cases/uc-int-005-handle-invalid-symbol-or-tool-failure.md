---
doc_id: CAP-INT-ORC-UC-005
title: "UC-INT-005: Handle Invalid Symbol or Tool Execution Failure"
doc_type: specification
plane: intelligence-plane
scope_level: use-case
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/tools/gateway.py"
related_docs:
  - CAP-INT-ORC-REQ-001
  - CAP-INT-ORC-ERR-001
  - DIAG-INT-ORC-STATE-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Specified UC-INT-005 Handle Invalid Symbol or Tool Execution Failure."
---

# UC-INT-005: Handle Invalid Symbol or Tool Execution Failure

| Attribute | Value |
|---|---|
| **Use Case ID** | `UC-INT-005` |
| **Primary Actor** | `MarketIntelligenceGraph` / `ControlledToolGateway` |
| **Supporting Actors** | `PlatformRuntimeContainer` |
| **Trigger** | Investigation submitted with unmonitored `symbol` OR tool execution raises error/timeout. |
| **Preconditions** | `AgentWorkflowState` initialized. |
| **Postconditions** | Unmonitored symbol -> `status = "FAILED"` and `final_report = {"error": ...}`. Tool/Validator error -> exception propagates (`AS-IS` gap). |
| **Permissions** | N/A (Guardrail & failure path). |
| **State Transitions** | `QUEUED` -> `FAILED` (invalid symbol); `RUNNING` -> uncaught exception (`AS-IS` tool failure). |
| **Related Diagrams** | [workflow-state-diagram.md](../workflows/workflow-state-diagram.md), [agent-workflow-diagram.md](../workflows/agent-workflow-diagram.md) |
| **Relevant Contracts** | [error-catalog.md](../contracts/error-catalog.md) |

## Main Flow (Unmonitored Symbol — `AS-IS` Implemented)
1. Node 1 (`intake_and_guardrail_node`) normalizes `symbol = state.symbol.upper().strip()`.
2. `symbol not in self._monitored_symbols` evaluates to `True`.
3. Node 1 sets `state.status = "FAILED"` and `state.final_report = {"error": f"Symbol '{state.symbol}' is not in monitored catalog."}`.
4. `run_investigation()` returns immediately without calling planner or tools.

## Alternative & Exception Flows (Tool Execution Failure — `AS-IS` Gap)
- **Alt 1 (Tool Timeout / Limit / Auth Error)**: `ControlledToolGateway` raises `asyncio.TimeoutError`, `ToolQueryLimitExceededError`, or `UnauthorizedToolAccessError`. `MarketIntelligenceGraph` does **not** catch these inside Node 3; `state.status` remains `"RUNNING"` in `runtime.agent_runs[run_id]`.
- **Target Flow**: Catch tool/validator exceptions in `run_investigation()`, record structured error metadata, and transition `state.status = "FAILED"`.

## Business Rules & Acceptance Criteria
- Enforces `BR-INT-001`, `FR-INT-005`.
- **AC-INT-005**: Passing `"DOGEFAKEUSDT"` results in `status == "FAILED"`, `len(evidence_trail) == 0`, and `visited_nodes == ["intake_and_guardrail_node"]`.

## Open Questions
- `OPEN-INT-008`: Should transient tool timeouts trigger a single retry or immediately fail the step and allow the planner to continue?

