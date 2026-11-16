---
doc_id: CAP-INT-ORC-WF-001
title: "Workflow Specification: 5-Node Market Investigation Orchestration"
doc_type: specification
plane: intelligence-plane
scope_level: capability
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
    - "src/intelligence/workflows/investigation.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - INT-ARCH-RT-001
  - DIAG-INT-ORC-AGT-001
  - DIAG-INT-ORC-SEQ-001
  - DIAG-INT-ORC-STATE-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Specified the 5-node workflow execution semantics, loop exit predicates, and AS-IS vs TARGET asynchronous orchestration."
---

# Workflow Specification: 5-Node Market Investigation Orchestration

Derived visual workflows: [agent-workflow-diagram.md](agent-workflow-diagram.md) (`DIAG-INT-ORC-AGT-001`), [agent-run-sequence.md](agent-run-sequence.md) (`DIAG-INT-ORC-SEQ-001`), [workflow-state-diagram.md](workflow-state-diagram.md) (`DIAG-INT-ORC-STATE-001`).

## 1. Workflow Nodes & Guard Transitions (`AS-IS`)

| Step | Node Name (`WORKFLOW_NODES`) | Entry Condition | Action & State Mutations | Exit Transition |
|---|---|---|---|---|
| 1 | `intake_and_guardrail_node` | `status == "QUEUED"` | Uppercase/strip `symbol`; verify membership in `_monitored_symbols`. | If invalid -> `status="FAILED"` (return); else `status="RUNNING"` -> Step 2. |
| 2 | `investigation_planner_node` | `can_continue_planning()` is `True` | Call `_llm.plan_tool_sequence(state)`; add `plan_tokens` to `tokens_consumed`; increment `current_iteration`. | If `planned_tools` empty -> break to Step 5; else -> Step 3. |
| 3 | `tool_gateway_executor_node` | Non-empty `planned_tools` | Sequentially `await _gateway.execute_tool(...)` with hardcoded `_agent_permissions`; append envelopes to `evidence_trail`. | Step 4 (or unhandled exception on error `AS-IS`). |
| 4 | `evidence_verifier_node` | Step 3 completed | Check `len(state.evidence_trail) >= 3`. | If `>= 3` -> break to Step 5; else re-evaluate `while can_continue_planning()` -> Step 2 or Step 5. |
| 5 | `report_synthesizer_node` | Loop exited while `status == "RUNNING"` | Call `_llm.synthesize_narrative(state)` (`+540` tokens); run `ReportValidator.validate_report()`; call `generate_analysis_report`; set `final_report`, `status="COMPLETED"`. | Terminal `COMPLETED` (or unhandled `ReportProvenanceError`). |

## 2. Trigger Modes & Asynchronous Target (`AS-IS` vs `TARGET`)

- **`ON_DEMAND` (`AS-IS`)**: Triggered via `PlatformRuntimeContainer.execute_agent_investigation()` inside `POST /api/v1/agents/runs` handler. Executes Steps 1–5 synchronously before returning HTTP `202`.
- **`EVENT_TRIGGERED` (`TARGET — NOT_IMPLEMENTED`)**: Data Plane `StatisticalAnomalyDetector` emits `EventEnvelopeV1` to `market.anomalies.v1` with 900s cooldown; `TARGET` `agent-worker` consumes this topic and invokes the identical 5-node workflow outside HTTP threads. Currently, no Kafka consumer exists in `src/intelligence/`.

