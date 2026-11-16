---
doc_id: CAP-INT-ORC-REQ-001
title: "Capability Specification: Market Intelligence Workflow & Tool Gateway"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: business-analyst
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
    - "src/intelligence/main.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-RULE-001
  - CAP-INT-ORC-NFR-001
  - CAP-APP-AGT-REQ-001
  - OVR-REQ-001
requirement_ids:
  - BR-INT-001
  - BR-INT-002
  - FR-INT-001
  - FR-INT-002
  - FR-INT-003
  - FR-INT-004
  - FR-INT-005
  - FR-INT-006
  - FR-INT-007
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Authored capability business needs, functional requirements (FR-INT-001..007), AS-IS vs TARGET matrix, and open questions."
---

# Capability Specification: Market Intelligence Workflow & Tool Gateway

## 1. Business Needs & Scope Boundary

| Business Need ID | Business Outcome | Upstream Trace | Status |
|---|---|---|---|
| `BR-INT-001` | Produce auditable, quantitative market investigation reports over spot market and analytical stores without permitting LLM SQL execution or prompt arithmetic. | `BR-SYS-003` (`OVR-REQ-001`) | `DRAFT` (`SIMULATED`) |
| `BR-INT-002` | Contain agent runtime resource consumption, tool side effects, and unauthorized tool access behind deterministic policy guardrails and isolated worker execution. | `BR-SYS-003`, `ADR-OVR-003` | `DRAFT` (`PARTIALLY_IMPLEMENTED`) |

## 2. Functional Requirements (`FR-INT-*`)

| Req ID | Requirement Statement | `AS-IS` Evidence (`Code / Test`) | `TARGET` State & Verified Gap |
|---|---|---|---|
| `FR-INT-001` | Workflow intake MUST validate and normalize `symbol` against monitored instruments before running planning nodes, transitioning invalid symbols directly to `FAILED`. | `graph.py:122-128`; `test_three_planes_framework.py:346-353` | `IMPLEMENTED` with drift: `monitored_symbols` is a static tuple captured at `PlatformRuntimeContainer.__init__` and does not reflect dynamic catalog updates. |
| `FR-INT-002` | Orchestrator MUST execute bounded investigation planning (`max_iterations`, planning token cap = `80%` of `token_budget`, `status == "RUNNING"`), terminating planning cleanly when evidence threshold or budget is reached. | `investigation.py:37-43`, `graph.py:131-155` | `PARTIALLY_IMPLEMENTED`: Pure Python `while` loop (`zero langgraph imports`); ignores `PlatformConfig` overrides; Node 5 executes outside budget guard. |
| `FR-INT-003` | Every tool call MUST pass through `ControlledToolGateway` enforcing `ApprovedAgentTool` whitelist, `required_permission`, `max_rows_or_periods` cap, and `asyncio.wait_for` timeout, attaching `ToolProvenanceMetadata`. | `gateway.py:44-97`; `test_contracts_and_guardrails.py:151-184` | `PARTIALLY_IMPLEMENTED`: No input JSON/Pydantic schema validation; negative/zero limits unchecked; missing handlers return `stub_ok`; timeouts/denials not recorded in `_audit_log`. |
| `FR-INT-004` | Quantitative tools (`calculate_returns`, `calculate_volatility`, `calculate_correlation`, `detect_anomalies`) MUST compute results via deterministic Python functions (`src/shared/domain/quant.py` / `StatisticalAnomalyDetector`). | `runtime.py:450-501`, `quant.py:8-54` | `SIMULATED`: Reads in-memory `ClickHouseBatchSink` or silent static fallback arrays (`[89500.0, ...]`); ignores `lookback_periods` slicing; `detect_anomalies` mutates cooldown state. |
| `FR-INT-005` | Report synthesis MUST validate citations via `ReportValidator` before persisting `StructuredAnalysisReport` via `generate_analysis_report`. | `graph.py:158-171`, `validator.py:18-31`; `test_three_planes_framework.py:355-371` | `PARTIALLY_IMPLEMENTED`: Validates `invocation_id` membership only (no numeric cross-check); persists to in-memory `runtime.reports` only (Postgres `agent_runs` unwired). |
| `FR-INT-006` | `agent-worker` MUST execute `ON_DEMAND` queued runs and `EVENT_TRIGGERED` anomaly alerts asynchronously in an isolated worker process with durable PostgreSQL checkpoints. | `main.py:12-22`, `deploy/postgres/init/01_schema.sql:41-66` | `NOT_IMPLEMENTED`: `src/intelligence/main.py` logs settings and exits; `POST /api/v1/agents/runs` runs inline synchronously; zero `market.anomalies.v1` Kafka consumer exists. |
| `FR-INT-007` | External LLM adapter (`TARGET`) MUST obey a typed async adapter interface, prompt separation, real token accounting, provider timeouts, and deterministic failure handling without altering `ControlledToolGateway` guarantees. | `graph.py:14-97`, `.env.example:88-90` | `SIMULATED`: Only `DeterministicMockLLMAdapter` exists; `LLM_PROVIDER`, `LLM_MODEL_NAME`, and `LLM_API_KEY` are not loaded in `PlatformConfig`. |

## 3. Open Questions & Blockers

- **`OPEN-INT-001`**: External LLM provider choice, privacy/retention constraints, and fallback policy when provider returns errors (`BR-SYS-003`).
- **`OPEN-INT-002`**: Side-effect separation for `detect_anomalies` (read-only dry-run evaluation for agents vs alert emission cooldown mutation).
- **`OPEN-INT-003`**: Scope of semantic/numeric verification required in `ReportValidator` prior to enabling non-mock LLMs.
- **`OPEN-INT-004`**: Aligning `run_id` UUID format and Postgres DDL (`agent_runs` / `agent_tool_invocations`) for durable state & idempotency.

