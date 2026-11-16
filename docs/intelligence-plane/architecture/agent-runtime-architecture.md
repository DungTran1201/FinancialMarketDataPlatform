---
doc_id: INT-ARCH-RT-001
title: "Agent Runtime & State Architecture"
doc_type: architecture
plane: intelligence-plane
scope_level: plane
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
    - "src/intelligence/main.py"
    - "src/serving/infrastructure/runtime.py"
    - "src/shared/config/settings.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - INT-ARCH-LLM-001
  - INT-ARCH-GW-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Detailed 5-node Python loop, state lifecycle, budget math, unconnected config timeouts, execution modes, and failure/persistence gaps."
---

# Agent Runtime & State Architecture

## 1. Runtime Entrypoints (`AS-IS` vs `TARGET`)

- **Active Entrypoint (`AS-IS`)**: `PlatformRuntimeContainer.execute_agent_investigation()` (`src/serving/infrastructure/runtime.py:555-597`), invoked inline by `POST /api/v1/agents/runs`. It checks `self.idempotency_keys`, creates `AgentWorkflowState`, stores it in `self.agent_runs[run_id]`, and awaits `self.intelligence_graph.run_investigation(state)`.
- **Worker Entrypoint (`src/intelligence/main.py`)**: `main()` loads `PlatformConfig`, logs `max_iterations`, `tool_timeout`, and `max_tokens`, and returns immediately. It does **not** run an event loop, poll PostgreSQL `agent_runs`, or consume Kafka `market.anomalies.v1`.

## 2. Workflow Engine & 5-Node Execution Loop

Although `graph.py` and `pyproject.toml` (`intelligence = ["langgraph>=0.1.0", "numpy>=1.26.4"]`) reference LangGraph, `src/intelligence/` contains **zero `langgraph` imports**. `MarketIntelligenceGraph.run_investigation()` executes a deterministic Python `while` loop across `WORKFLOW_NODES`:

1. **`intake_and_guardrail_node`**: Appends node name, normalizes `symbol = state.symbol.upper().strip()`, checks membership in `self._monitored_symbols` (`("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT")`). On mismatch, sets `status = "FAILED"`, writes `final_report = {"error": ...}`, and returns immediately. Otherwise sets `status = "RUNNING"`.
2. **`investigation_planner_node`** *(inside `while state.can_continue_planning()`)*: Calls `self._llm.plan_tool_sequence(state)`, adds `plan_tokens` to `tokens_consumed`, increments `current_iteration`. Breaks loop if `planned_tools` is empty.
3. **`tool_gateway_executor_node`** *(inside loop)*: Iterates `planned_tools` sequentially, calling `await self._gateway.execute_tool(...)` with hardcoded `self._agent_permissions = frozenset({"market:read", "historical:read", "analytics:read", "agent:trigger"})`, appending each `ToolExecutionEnvelope` to `state.evidence_trail`.
4. **`evidence_verifier_node`** *(inside loop)*: Appends node name; if `len(state.evidence_trail) >= 3`, breaks out of the planning loop.
5. **`report_synthesizer_node`** *(outside loop)*: Calls `self._llm.synthesize_narrative(state)`, adds `synth_tokens` (`540`) to `tokens_consumed`, runs `ReportValidator.validate_report(report, state.evidence_trail)`, invokes `ApprovedAgentTool.GENERATE_ANALYSIS_REPORT` via `ControlledToolGateway` (appending an 8th envelope to `evidence_trail`), sets `state.final_report = report`, and sets `state.status = "COMPLETED"`.

## 3. State Lifecycle, Budgets & Timeouts

- **State Schema (`AgentWorkflowState`)**: `run_id`, `trigger_mode` (`ON_DEMAND | EVENT_TRIGGERED`), `symbol`, `prompt_summary`, `max_iterations=6`, `token_budget=8000`, `current_iteration=0`, `tokens_consumed=0`, `planned_tools`, `evidence_trail`, `visited_nodes`, `final_report`, `status` (starts `"QUEUED"`, transitions to `"RUNNING"`, then `"COMPLETED"` or `"FAILED"`).
- **Iteration & Token Budgets**: `can_continue_planning()` returns `True` iff `current_iteration < max_iterations` (`6`), `tokens_consumed < int(token_budget * 0.8)` (`6400`), and `status == "RUNNING"`.
  - **Config Discrepancy**: `PlatformRuntimeContainer.execute_agent_investigation()` instantiates `AgentWorkflowState` with default `(6, 8000)` instead of passing `PlatformConfig.agent_max_iterations` / `agent_max_tokens_per_run`.
  - **Post-Loop Budget Bypass**: `report_synthesizer_node` runs outside `can_continue_planning()` and adds `540` tokens unconditionally.
- **Timeouts**:
  - Per-tool timeout (`1.5s`–`8.0s`) is enforced by `ControlledToolGateway` via `asyncio.wait_for()`.
  - `AGENT_RUN_TIMEOUT_SECONDS=90` in `.env.example` is **not loaded** in `PlatformConfig` (`src/shared/config/settings.py`) and is **not enforced** around `run_investigation()`.

## 4. Run Modes, Worker Isolation & Failure Handling

- **Execution Modes**: `ON_DEMAND` runs synchronously inline on HTTP `POST /api/v1/agents/runs`. `EVENT_TRIGGERED` is accepted as a string parameter but has **no Kafka consumer** (`NOT_IMPLEMENTED`).
- **Worker Isolation**: `TARGET` places `agent-worker` in a separate container (`--profile intelligence`, `deploy/docker` + `docker-compose.yml`). `AS-IS`, execution shares the FastAPI process memory and event loop.
- **Failure Handling (`AS-IS`)**:
  - Unmonitored symbol -> `status = "FAILED"` (clean return).
  - Uncaught exceptions from `ControlledToolGateway` (`UnauthorizedToolAccessError`, `ToolQueryLimitExceededError`, `asyncio.TimeoutError`) or `ReportValidator` (`ReportProvenanceError`) propagate out of `run_investigation()` without setting `state.status = "FAILED"` or catching inside the node loop.
- **Persistence & Recovery**:
  - `AS-IS`: Purely in-memory (`runtime.agent_runs`, `runtime.reports`). Process restart loses all state.
  - `TARGET`: Persist state checkpoints and final reports to PostgreSQL `agent_runs` and `agent_tool_invocations` (`deploy/postgres/init/01_schema.sql`), enabling worker recovery and true async `202` queuing.
