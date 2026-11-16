---
doc_id: INT-ARCH-RT-001
title: "Agent Runtime & State Lifecycle Architecture"
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
    - "src/intelligence/main.py"
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/serving/infrastructure/runtime.py"
    - "src/serving/api/modules/agent_api/presentation/router.py"
    - "src/shared/config/settings.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - CAP-INT-ORC-WF-001
  - DIAG-INT-ORC-STATE-001
  - DIAG-INT-ORC-AGT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Detailed AS-IS pure Python workflow loop, stubbed agent-worker entrypoint, disconnected config bounds, failure modes, and TARGET LangGraph worker architecture."
---

# Agent Runtime & State Lifecycle Architecture

Derived diagrams: [workflow-state-diagram.md](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/workflows/workflow-state-diagram.md) (`DIAG-INT-ORC-STATE-001`) and [agent-workflow-diagram.md](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/workflows/agent-workflow-diagram.md) (`DIAG-INT-ORC-AGT-001`).

## 1. Scope and Runtime Entrypoints (`AS-IS` vs `TARGET`)

### 1.1 Scope

This specification defines the execution engine, state transitions, resource budgets, timeouts, run modes, process isolation, and recovery mechanics of the Intelligence Plane workflow runtime.

### 1.2 Agent Runtime Entrypoint (`src/intelligence/main.py`)

- **`AS-IS` Stub Behavior**: `docker-compose.yml` (`--profile intelligence`, service `agent-worker`) launches `python -m src.intelligence.main`. In `src/intelligence/main.py:12-22`, `main()` instantiates `PlatformConfig()`, configures Python `logging`, logs `Initialized agent-worker (max_iterations=%d, tool_timeout=%.1fs, max_tokens=%d)`, and immediately returns (container exits with code `0`).
- **Actual `AS-IS` Execution Path**: All runs execute in-process inside `PlatformRuntimeContainer.execute_agent_investigation()` (`src/serving/infrastructure/runtime.py:555-597`), invoked synchronously by FastAPI `POST /api/v1/agents/runs` (`src/serving/api/modules/agent_api/presentation/router.py:45-75`) or `svc-intelligence-agent` (`src/serving/api/services/intelligence.py`).
- **`TARGET` Worker Behavior**: `agent-worker` MUST run a persistent asyncio supervision loop polling PostgreSQL `agent_runs` (`status = 'QUEUED'`) and consuming Kafka `market.anomalies.v1`, executing workflows asynchronously outside HTTP request lifetimes.

## 2. Context and Execution Modes

| Execution Mode / Aspect | `AS-IS` Reality | `TARGET` Design |
|---|---|---|
| **`ON_DEMAND` (HTTP Trigger)** | `POST /api/v1/agents/runs` awaits full `run_investigation(state)` completion before sending HTTP `202` (`status` is already `COMPLETED` or `FAILED`). | `POST /api/v1/agents/runs` inserts `QUEUED` ticket and returns `202` immediately; SSE streams live transitions. |
| **`EVENT_TRIGGERED` (Kafka Anomaly)** | Accepts `trigger_mode="EVENT_TRIGGERED"` string only if supplied to `POST /api/v1/agents/runs` or `AgentWorkflowState(...)`; no Kafka consumer exists. | `agent-worker` consumes `EventEnvelopeV1` from `market.anomalies.v1` and enqueues bounded investigations subject to 900s cooldown. |
| **Idempotency** | Application Plane `runtime.idempotency_keys` dict deduplicates `Idempotency-Key` header in memory (`runtime.py:563-575`); Postgres `agent_runs` lacks an `idempotency_key` column. | Unique partial index on `agent_runs(idempotency_key)` in PostgreSQL. |

## 3. Building Blocks: Workflow Graph Engine and Nodes

### 3.1 Pure Python Loop (`AS-IS`) vs LangGraph (`TARGET`)

Although docstrings in `main.py`, `graph.py`, and `investigation.py` describe a "LangGraph" workflow and `pyproject.toml` declares `langgraph>=0.1.0` under optional extra `[intelligence]`, **`src/intelligence/` contains zero `langgraph` imports**. `MarketIntelligenceGraph.run_investigation()` (`src/intelligence/orchestrator/graph.py:119-172`) executes a sequential Python `async` method containing a `while state.can_continue_planning():` loop.

### 3.2 The Five Workflow Nodes (`WORKFLOW_NODES`)

Defined in `src/intelligence/workflows/investigation.py:10-16`:

1. **`intake_and_guardrail_node` (`graph.py:122-128`)**: Appends node name to `visited_nodes`, normalizes `state.symbol = state.symbol.upper().strip()`, validates membership in `self._monitored_symbols` (static tuple captured at container init: `BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, `XRPUSDT`). If absent, sets `status="FAILED"`, writes `final_report={"error": ...}`, and returns early; otherwise sets `status="RUNNING"`.
2. **`investigation_planner_node` (`graph.py:133-140`)**: Calls `self._llm.plan_tool_sequence(state)`, adds returned `plan_tokens` to `state.tokens_consumed`, sets `state.planned_tools`, and increments `state.current_iteration`. Breaks loop if `planned_tools` is empty.
3. **`tool_gateway_executor_node` (`graph.py:143-150`)**: Iterates sequentially over `state.planned_tools`, invoking `await self._gateway.execute_tool(...)` with hardcoded `self._agent_permissions`, appending each `ToolExecutionEnvelope` to `state.evidence_trail`.
4. **`evidence_verifier_node` (`graph.py:153-155`)**: Breaks the `while` loop as soon as `len(state.evidence_trail) >= 3`. Does NOT inspect tool status, quality, or relevance; simply acts as a minimum-evidence exit condition.
5. **`report_synthesizer_node` (`graph.py:158-172`)**: Runs **outside** the `while` loop. Calls `self._llm.synthesize_narrative(state)`, adds `synth_tokens` (`540`) to `tokens_consumed`, invokes `ReportValidator.validate_report(report, state.evidence_trail)`, persists via Tool #10 (`generate_analysis_report`), assigns `state.final_report = report`, and transitions `state.status = "COMPLETED"`.

## 4. State Lifecycle, Budgets, and Timeouts

### 4.1 `AgentWorkflowState` Fields & Transitions

Defined in `src/intelligence/workflows/investigation.py:19-35`:

- **Initial Status**: `"QUEUED"` (`AgentWorkflowState` default).
- **Transitions (`AS-IS`)**:
  - `QUEUED -> RUNNING` (Node 1 succeeds).
  - `QUEUED -> FAILED` (Node 1 rejects unmonitored symbol).
  - `RUNNING -> COMPLETED` (Node 5 succeeds).
  - **Missing Transitions (`GAP`)**: `"CANCELLED"` (present in PostgreSQL `agent_runs` CHECK constraint) and exception-caught `"FAILED"` during Nodes 2–5 are NOT implemented (`runtime.py` has no `try/except` around `run_investigation()`, so uncaught `UnauthorizedToolAccessError`, `TimeoutError`, or `ReportProvenanceError` bubble up as HTTP 500 and leave `state.status == "RUNNING"` in `runtime.agent_runs`!).

### 4.2 Iteration, Token Budgets, and Timeouts

| Control Parameter | Defined In | `AS-IS` Enforcement | Verified Discrepancies |
|---|---|---|---|
| `max_iterations` | `AgentWorkflowState` (`6`) & `PlatformConfig.agent_max_iterations` (`6`) | Checked in `can_continue_planning()` (`current_iteration < max_iterations`). | `PlatformRuntimeContainer.execute_agent_investigation()` does **not** pass `self.config.agent_max_iterations` into `AgentWorkflowState`, so `AGENT_MAX_ITERATIONS` env overrides are ignored! |
| `token_budget` | `AgentWorkflowState` (`8000`) & `PlatformConfig.agent_max_tokens_per_run` (`8000`) | Planning stops when `tokens_consumed >= int(token_budget * 0.8)` (`6400`), reserving 20% (`1600`) for synthesis. | `PlatformConfig.agent_max_tokens_per_run` is never passed to `AgentWorkflowState`; Node 5 `synthesize_narrative()` executes unconditionally outside the budget guard and adds `540` tokens even if budget was already exceeded. |
| **Per-Tool Timeout** | `ToolGovernancePolicy.timeout_seconds` (`1.5s`–`8.0s`) & `PlatformConfig.agent_tool_timeout_seconds` (`5.0s`) | Enforced via `asyncio.wait_for(handler(params), timeout=policy.timeout_seconds)` in `ControlledToolGateway`. | `PlatformConfig.agent_tool_timeout_seconds` is ignored by `ControlledToolGateway`; `TimeoutError` is unhandled by Node 3. |
| **Whole-Run Timeout** | `.env.example` `AGENT_RUN_TIMEOUT_SECONDS=90` | **NOT_IMPLEMENTED** (`PlatformConfig` does not parse it; `run_investigation()` has no outer `asyncio.wait_for`). | An external LLM hang in `TARGET` mode would block indefinitely without an outer run timeout. |

## 5. Worker Isolation, Persistence, and Recovery

- **Process & Failure Isolation (`AS-IS`)**: Because `MarketIntelligenceGraph` runs inside the FastAPI event loop, an unhandled exception or CPU spike affects API serving, and `svc-intelligence-agent` (`:8006`) holds an isolated `PlatformRuntimeContainer` that cannot see runs created on `backend-api` (`:8000`).
- **Persistence & Crash Recovery (`AS-IS`)**: State lives solely in `runtime.agent_runs: dict[str, AgentWorkflowState]` and `runtime.reports: dict[str, StructuredAnalysisReport]`. Restarting the process wipes all history, leaving zero checkpoint recovery.
- **`TARGET` Persistence & Recovery**: Persist `AgentWorkflowState` checkpoints per node in PostgreSQL (`agent_runs` + `agent_tool_invocations` or LangGraph Postgres checkpointer), reclaim stale `RUNNING` leases on worker restart using heartbeat timestamps, and mark runs exceeding `AGENT_RUN_TIMEOUT_SECONDS` as `FAILED` safely.
