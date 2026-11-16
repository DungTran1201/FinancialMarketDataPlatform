---
doc_id: CAP-INT-ORC-AGT-001
title: "AI Agent Specification: Market Intelligence Workflow & Tool Gateway"
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
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-REQ-001
  - INT-ARCH-LLM-001
  - INT-ARCH-GW-001
  - DIAG-INT-ORC-AGT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Authored TPL-ARCH-AGENT-001 compliant AI Agent specification covering runtime, 5-node transitions, 10 tools with side effects, memory, and evals."
---

# AI Agent Specification: Market Intelligence Workflow & Tool Gateway

Derived workflow graph: [agent-workflow-diagram.md](../workflows/agent-workflow-diagram.md) (`DIAG-INT-ORC-AGT-001`). Authoritative tool schemas: [tool-contracts.yaml](../../../../../shared-contracts/tool-contracts.yaml).

## 1. Agent Runtime & LLM Integration

- **Orchestrator & Runtime (`AS-IS` vs `TARGET`)**: `MarketIntelligenceGraph` runs a pure Python `async` `while` loop (`src/intelligence/orchestrator/graph.py:131-155`) inline inside FastAPI `PlatformRuntimeContainer`. `src/intelligence/main.py` (`agent-worker`) is a stub that logs configuration and exits; zero `langgraph` imports exist in `src/intelligence/`. `TARGET` runtime migrates to a `langgraph` `StateGraph` inside an isolated `agent-worker` consuming Postgres `agent_runs` and Kafka `market.anomalies.v1`.
- **LLM Adapter (`AS-IS` vs `TARGET`)**: `AS-IS` injects `DeterministicMockLLMAdapter` (`LLM_PROVIDER=mock`), emitting a deterministic 7-tool plan (`420` tokens) on iteration 0 and fixed narrative dict (`540` tokens) regardless of `prompt_summary`. `TARGET` adds an async `LLMAdapterPort` for external providers (`LLM_PROVIDER`, `LLM_MODEL_NAME`, `LLM_API_KEY` — currently unwired in `PlatformConfig`).
- **Execution Caps**: `AgentWorkflowState` defaults `max_iterations=6`, `token_budget=8000` (planning ceiling `6400`), per-tool timeouts `1.5s`–`8.0s` via `asyncio.wait_for`. Note: `AGENT_RUN_TIMEOUT_SECONDS=90` and `PlatformConfig.agent_*` overrides are not wired `AS-IS`.

## 2. Workflow Graph & State Transitions

| Node ID | Responsibility | Allowed State Transitions | Loop / Exit Guard |
|---|---|---|---|
| `intake_and_guardrail_node` | Normalize `symbol` and check `_monitored_symbols` | `QUEUED -> RUNNING` or `QUEUED -> FAILED` | Rejects unmonitored symbol immediately |
| `investigation_planner_node` | Select next tool batch & account planning tokens | `RUNNING -> tool_gateway_executor_node` or break to Node 5 | `can_continue_planning()` (`iter < 6` & `tokens < 6400` & `RUNNING`); breaks if `planned_tools == []` |
| `tool_gateway_executor_node` | Dispatch tools sequentially via `ControlledToolGateway` | `RUNNING -> evidence_verifier_node` | Whitelist, RBAC, `max_rows_or_periods`, per-tool `timeout_seconds` |
| `evidence_verifier_node` | Check evidence count sufficiency (`>= 3`) | Loop to Node 2 or exit to Node 5 | Breaks loop when `len(evidence_trail) >= 3` |
| `report_synthesizer_node` | Synthesize narrative, run `ReportValidator`, persist via Tool #10 | `RUNNING -> COMPLETED` | Runs outside `can_continue_planning()`; `ReportProvenanceError` aborts before persistence |

## 3. Tool Contracts, Permissions & Side-Effect Controls

Full JSON/YAML schemas live in [tool-contracts.yaml](../../../../../shared-contracts/tool-contracts.yaml). Summary of modes and side-effect discrepancies:

| Tool Name | Actual Mode (`AS-IS`) | Required Permission | Hard Bounds (`Max / Timeout`) | Side Effects & Approval Status | Backing Store (`Policy` vs `AS-IS`) |
|---|---|---|---|---|---|
| `get_latest_price` | `READ_ONLY` | `market:read` | `1 / 1.5s` | None | Policy: Redis+CH / `AS-IS`: In-mem Redis+CH fallback |
| `get_market_snapshot` | `READ_ONLY` | `market:read` | `1 / 2.0s` | None | Policy: Redis+CH / `AS-IS`: In-mem Redis only |
| `get_historical_candles` | `READ_ONLY` | `historical:read` | `500 / 5.0s` | None | Policy: CH RO / `AS-IS`: In-mem `_klines_table` |
| `get_market_statistics` | `READ_ONLY` | `analytics:read` | `1 / 5.0s` | None | Policy: CH MV RO / `AS-IS`: In-mem scan |
| `calculate_returns` | `READ_ONLY` | `analytics:read` | `720 / 5.0s` | None | Policy: CH RO+Math / `AS-IS`: In-mem or static fallback |
| `calculate_volatility` | `READ_ONLY` | `analytics:read` | `720 / 5.0s` | None | Policy: CH RO+Math / `AS-IS`: In-mem or static fallback |
| `calculate_correlation` | `READ_ONLY` | `analytics:read` | `2160 / 8.0s` | None | Policy: CH RO+Math / `AS-IS`: In-mem or static fallback |
| `detect_anomalies` | `STATE_MUTATING` | `analytics:read` | `168 / 5.0s` | Mutates 900s cooldown & `detected_anomalies`; no approval gate (`GAP`) | Policy: CH RO+Math / `AS-IS`: In-mem or static + `anomaly_detector` |
| `get_data_freshness` | `READ_ONLY` | `market:read` | `1 / 3.0s` | None | Policy: Redis+CH meta / `AS-IS`: `latest_price_handler` |
| `generate_analysis_report` | `WRITE` | `agent:trigger` | `1 / 3.0s` | Writes `runtime.reports[run_id]`; `is_read_only_market_data=True` bug (`GAP`) | Policy: Postgres RW / `AS-IS`: In-mem `runtime.reports` |

## 4. Memory, Provenance & Hallucination Controls

- **State & Audit Persistence**: `AS-IS` keeps `AgentWorkflowState` in `runtime.agent_runs`, reports in `runtime.reports`, and successful tool calls in `ControlledToolGateway._audit_log`. PostgreSQL `agent_runs` and `agent_tool_invocations` (`01_schema.sql`) are unwired.
- **Provenance Enforcement**: `ReportValidator.validate_report()` checks only non-empty `provenance_citations` and `invocation_id` membership in `evidence_trail`. It does **not** cross-check numeric values in narrative `summary` or verify citation metadata fields (`OPEN-INT-003`).

## 5. Evaluation, Observability & Safety Testing

- **Evaluation Criteria (`AS-IS` vs `TARGET`)**: `AS-IS` runs offline deterministic integration tests (`test_three_planes_framework.py`) and gateway contract tests (`test_contracts_and_guardrails.py`). `TARGET` requires golden dataset evals, numeric-consistency validation, and per-node/tool latency Prometheus instrumentation (`INT-ARCH-EVAL-001`).
- **Abuse / Safety Tests**: Covers unwhitelisted tool rejection, missing permission denial, and row-limit rejection (`test_contracts_and_guardrails.py`); timeout tests, negative limit tests, and prompt-injection tests (`TARGET` external LLM) are currently missing (`NOT_IMPLEMENTED`).
