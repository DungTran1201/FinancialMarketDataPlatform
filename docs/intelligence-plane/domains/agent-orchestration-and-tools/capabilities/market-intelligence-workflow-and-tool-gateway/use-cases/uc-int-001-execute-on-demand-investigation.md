---
doc_id: CAP-INT-ORC-UC-001
title: "UC-INT-001: Execute On-Demand Market Investigation"
doc_type: specification
plane: intelligence-plane
scope_level: use-case
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - CAP-INT-ORC-REQ-001
  - DIAG-INT-ORC-SEQ-001
  - DIAG-INT-ORC-FLOW-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Specified UC-INT-001 Execute On-Demand Market Investigation."
---

# UC-INT-001: Execute On-Demand Market Investigation

| Attribute | Value |
|---|---|
| **Use Case ID** | `UC-INT-001` |
| **Primary Actor** | Application Plane (`CAP-APP-AGT-001` via `PlatformRuntimeContainer`) |
| **Supporting Actors** | `MarketIntelligenceGraph`, `DeterministicMockLLMAdapter` (`AS-IS`), `ControlledToolGateway`, `ReportValidator` |
| **Trigger** | `await runtime.execute_agent_investigation(symbol, prompt_summary, trigger_mode="ON_DEMAND", idempotency_key)` |
| **Preconditions** | `ControlledToolGateway` has all 10 handlers registered; `symbol` is non-empty string. |
| **Postconditions** | `AgentWorkflowState` reaches `COMPLETED` (with `final_report` in `runtime.reports`) or `FAILED`. |
| **Permissions** | Hardcoded `_agent_permissions = {"market:read", "historical:read", "analytics:read", "agent:trigger"}` (`AS-IS`). |
| **State Transitions** | `QUEUED` -> `RUNNING` -> `COMPLETED` (or `QUEUED` -> `FAILED` on unmonitored symbol). |
| **Related Diagrams** | [agent-run-sequence.md](../workflows/agent-run-sequence.md), [agent-workflow-diagram.md](../workflows/agent-workflow-diagram.md), [workflow-state-diagram.md](../workflows/workflow-state-diagram.md) |
| **Relevant Contracts** | `tool-contracts.yaml` (tools 1, 2, 3, 5, 6, 8, 9, 10) |

## Main Flow (`AS-IS`)
1. `PlatformRuntimeContainer` checks `idempotency_keys`; if present, returns existing `(AgentRunTicket, AgentWorkflowState)`.
2. Otherwise creates `AgentWorkflowState(status="QUEUED")`, stores in `runtime.agent_runs[run_id]`, and awaits `MarketIntelligenceGraph.run_investigation(state)`.
3. **Node 1 (`intake_and_guardrail_node`)**: Normalizes `symbol` and validates against `_monitored_symbols`; sets `status="RUNNING"`.
4. **Node 2 (`investigation_planner_node`)**: `DeterministicMockLLMAdapter.plan_tool_sequence()` returns 7 tools and `420` tokens.
5. **Node 3 (`tool_gateway_executor_node`)**: Executes all 7 tools sequentially via `ControlledToolGateway`, appending 7 envelopes to `evidence_trail`.
6. **Node 4 (`evidence_verifier_node`)**: Sees `len(evidence_trail) >= 3` (`7 >= 3`) and breaks loop.
7. **Node 5 (`report_synthesizer_node`)**: Synthesizes report (`540` tokens), validates citations via `ReportValidator`, persists via `generate_analysis_report` (8th envelope), sets `status="COMPLETED"`.

## Alternative & Exception Flows
- **Alt 1 (Idempotent Replay)**: Matching `Idempotency-Key` returns cached `run_id` without re-running the graph.
- **Exc 1 (Unmonitored Symbol)**: Covered in [UC-INT-005](uc-int-005-handle-invalid-symbol-or-tool-failure.md); Node 1 sets `status="FAILED"`.
- **Exc 2 (Gateway/Validator Error)**: Exceptions propagate uncaught from `run_investigation()` (`AS-IS` gap).

## Business Rules & Acceptance Criteria
- Enforces `BR-INT-001`..`BR-INT-005`.
- **AC-INT-001**: A valid `BTCUSDT` run records all 5 `visited_nodes`, `8` `evidence_trail` items, `7` `provenance_citations`, and `status == "COMPLETED"`.

## Open Questions
- `OPEN-INT-004`: When moving to async `agent-worker`, should `POST /api/v1/agents/runs` enqueue `QUEUED` and return immediately?

