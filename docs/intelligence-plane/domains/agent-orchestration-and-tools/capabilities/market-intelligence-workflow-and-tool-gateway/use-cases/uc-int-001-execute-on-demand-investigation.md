---
doc_id: CAP-INT-ORC-UC-001
title: "Use Case UC-INT-001: Execute On-Demand Market Investigation"
doc_type: specification
plane: intelligence-plane
scope_level: use-case
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: business-analyst
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - CAP-INT-ORC-REQ-001
  - CAP-INT-ORC-WF-001
  - CAP-APP-AGT-UC-001
  - DIAG-INT-ORC-SEQ-001
  - DIAG-INT-ORC-AGT-001
requirement_ids:
  - UC-INT-001
  - AC-INT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Specified on-demand market investigation use case grounded in MarketIntelligenceGraph and PlatformRuntimeContainer."
---

# Use Case UC-INT-001: Execute On-Demand Market Investigation

## 1. Identification, Actors & Trigger

- **Use Case ID**: `UC-INT-001`
- **Primary Actor**: Application Plane (`CAP-APP-AGT-001` via `PlatformRuntimeContainer.execute_agent_investigation()`), acting on behalf of a Quant Analyst.
- **Supporting Actors**: `MarketIntelligenceGraph`, Model Adapter (`DeterministicMockLLMAdapter` `AS-IS`), `ControlledToolGateway`, `ReportValidator`, Data Plane In-Memory Stores.
- **Trigger**: Caller submits `symbol`, `prompt_summary`, `trigger_mode="ON_DEMAND"`, and optional `idempotency_key` (via `POST /api/v1/agents/runs` `AS-IS`).

## 2. Preconditions, Permissions & Input/Output

- **Preconditions**:
  - `PlatformRuntimeContainer` initialized with `ControlledToolGateway` handlers and `MarketIntelligenceGraph`.
  - `symbol` belongs to `monitored_symbols` (default: `BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, `XRPUSDT`).
- **Permissions**:
  - `TARGET`: Caller holds `agent:trigger` RBAC capability; granted tool capabilities match caller scopes.
  - `AS-IS`: HTTP route has zero auth `Depends` (`SEC-AUDIT-003`), and `MarketIntelligenceGraph` hardcodes `frozenset({"market:read", "historical:read", "analytics:read", "agent:trigger"})`.
- **Inputs**: `symbol: str`, `prompt_summary: str`, `trigger_mode: str = "ON_DEMAND"`, `idempotency_key: str | None`.
- **Outputs**: `(AgentRunTicket, AgentWorkflowState)` with `status="COMPLETED"`, `visited_nodes`, `tokens_consumed`, `evidence_trail` (8 envelopes `AS-IS`), and `final_report`.

## 3. Main, Alternative & Exception Flows

### 3.1 Main Flow (`AS-IS` Synchronous Execution)

1. `PlatformRuntimeContainer.execute_agent_investigation()` checks `self.idempotency_keys` (if `idempotency_key` provided and seen, skips execution and returns existing `AgentWorkflowState`).
2. Allocates `run_id = f"run_{uuid.uuid4().hex[:12]}"`, creates `AgentWorkflowState(status="QUEUED")`, and stores it in `self.agent_runs[run_id]`.
3. Awaits `self.intelligence_graph.run_investigation(state)` synchronously inline.
4. **Node 1 (`intake_and_guardrail_node`)**: Normalizes `symbol`, validates membership in `_monitored_symbols`, transitions `status = "RUNNING"`.
5. **Loop (`can_continue_planning()`)**:
   - **Node 2 (`investigation_planner_node`)**: Calls `self._llm.plan_tool_sequence(state)` (iteration 0 returns 7 tools and `420` tokens); increments `current_iteration` to `1`.
   - **Node 3 (`tool_gateway_executor_node`)**: Dispatches each planned tool sequentially through `ControlledToolGateway.execute_tool()` (`UC-INT-002`), appending 7 envelopes to `evidence_trail`.
   - **Node 4 (`evidence_verifier_node`)**: Observes `len(evidence_trail) >= 3` (`7 >= 3`) and breaks the planning loop.
6. **Node 5 (`report_synthesizer_node`)**: Calls `synthesize_narrative(state)` (`+540` tokens), verifies citations via `ReportValidator.validate_report()` (`UC-INT-003`), persists report via Tool #10 (`generate_analysis_report`, `UC-INT-004`), sets `state.final_report`, and transitions `status = "COMPLETED"`.

### 3.2 Alternative Flows

- **A1 (Idempotent Replay)**: Matching `idempotency_key` in `self.idempotency_keys` returns the existing `AgentRunTicket` and `AgentWorkflowState` without re-running tools.
- **A2 (Planner Returns Empty List)**: If `_llm.plan_tool_sequence()` returns `[]`, loop breaks early and Node 5 executes (note: if `evidence_trail` is empty, `ReportValidator` raises `ReportProvenanceError`).
- **A3 (`EVENT_TRIGGERED` Mode `TARGET`)**: `agent-worker` consumes `market.anomalies.v1` and runs the identical 5-node workflow asynchronously without an HTTP request (`NOT_IMPLEMENTED AS-IS`).

### 3.3 Exception Flows

- **E1 (Unmonitored Symbol)**: Node 1 sets `status = "FAILED"` and `final_report = {"error": ...}` (`UC-INT-005`).
- **E2 (Tool / Provenance Exception)**: `UnauthorizedToolAccessError`, `ToolQueryLimitExceededError`, `TimeoutError`, or `ReportProvenanceError` propagates unhandled out of `run_investigation()`, leaving `state.status == "RUNNING"` in `runtime.agent_runs` (`GAP`).

## 4. Business Rules, State Transitions, Tool Contracts & Acceptance Criteria

- **Business Rules**: `RULE-INT-001`, `RULE-INT-002`, `RULE-INT-003`, `RULE-INT-005`, `RULE-INT-006`.
- **State Transitions**: `QUEUED -> RUNNING -> COMPLETED` (or `QUEUED -> FAILED` in Node 1).
- **Relevant Tool Contracts**: All 10 tools in [tool-contracts.yaml](../../../../../shared-contracts/tool-contracts.yaml) (7 invoked in Step 5 + `generate_analysis_report` in Step 6).
- **Acceptance Criteria (`AC-INT-001`)**: Given monitored symbol `BTCUSDT`, workflow visits all 5 nodes, stays within `max_iterations` (`6`) and `token_budget` (`8000`), records 8 envelopes (`7` evidence + `1` report persistence), and sets `status="COMPLETED"`. Given duplicate `Idempotency-Key`, returns exact same `run_id`.
- **Related Diagrams**: [agent-run-sequence.md](../workflows/agent-run-sequence.md) (`DIAG-INT-ORC-SEQ-001`), [agent-workflow-diagram.md](../workflows/agent-workflow-diagram.md) (`DIAG-INT-ORC-AGT-001`), [workflow-state-diagram.md](../workflows/workflow-state-diagram.md) (`DIAG-INT-ORC-STATE-001`).
- **Open Questions**: `OPEN-INT-001` (external LLM mode), `GAP-INT-001` (true async worker queue vs inline await).
