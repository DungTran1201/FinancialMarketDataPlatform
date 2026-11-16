---
doc_id: INT-ARCH-001
title: "Intelligence Plane Architecture Description"
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
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
    - "src/intelligence/main.py"
    - "src/serving/infrastructure/runtime.py"
    - "tests/architecture/test_clean_architecture_boundaries.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-RT-001
  - INT-ARCH-LLM-001
  - INT-ARCH-GW-001
  - INT-ARCH-SEC-001
  - INT-ARCH-EVAL-001
  - OVR-ARCH-3P-001
  - OVR-ARCH-XPL-001
  - ADR-OVR-003
  - ADR-INT-0001
  - DIAG-INT-C4-001
  - DIAG-INT-DEP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Authored comprehensive Intelligence Plane architecture covering context, ownership boundaries, building blocks, AS-IS vs TARGET topology, and architectural gaps."
---

# Intelligence Plane Architecture Description

Derived visual views: [intelligence-c4-container.md](diagrams/intelligence-c4-container.md) (`DIAG-INT-C4-001`) and [intelligence-dependency-diagram.md](diagrams/intelligence-dependency-diagram.md) (`DIAG-INT-DEP-001`).

## 1. Scope and Ownership Boundaries

The **Intelligence Plane (`Plane C`)** owns autonomous quantitative market investigation orchestration, model adapter abstraction, deterministic tool governance, workflow state tracking, evidence provenance validation, report synthesis, safety guardrails, and agent execution observability (`src/intelligence/`).

### 1.1 In Scope (Owned by Intelligence Plane)

- **Workflow Orchestrator & State**: 5-node bounded investigation state machine (`WORKFLOW_NODES`, `AgentWorkflowState`, `MarketIntelligenceGraph`).
- **Model Adapter Abstraction**: Planning and narrative synthesis abstraction (`DeterministicMockLLMAdapter` `AS-IS`; external provider adapters `TARGET`).
- **Tool Registry & Gateway**: `ApprovedAgentTool` (10 approved tools), `APPROVED_TOOL_POLICIES`, and `ControlledToolGateway` enforcement (whitelist, RBAC check, row/period cap, asyncio timeout, provenance tagging, audit log).
- **Provenance & Validation**: `ToolExecutionEnvelope`, `ToolProvenanceMetadata`, and `ReportValidator` citation verification.
- **Standalone Worker Entrypoint**: `src/intelligence/main.py` (`agent-worker` container blueprint in `docker-compose.yml`).

### 1.2 Explicitly Out of Scope (Owned by Other Planes)

- **HTTP API Gateway, Auth & Portal UI (`Application Plane`, `CAP-APP-AGT-001`, `CAP-APP-IAM-001`)**: `/api/v1/agents/*` and `/api/v1/reports/*` FastAPI routers, `Idempotency-Key` index, SSE replay formatting, JWT/API key auth, and `#/ai-workspace` (`AiWorkspaceModule.ts`).
- **Market Data Acquisition, Event Contracts & Storage (`Data Plane`, `CAP-DP-ING-001`, `CAP-DP-STR-001`, `CAP-DP-STR-002`, `CAP-DP-LAK-001`)**: Binance collectors, `EventEnvelopeV1` / Kafka topics (including `market.anomalies.v1` schema and `StatisticalAnomalyDetector` producer), Redis hot state, ClickHouse OLAP tables, and Lakehouse Parquet/Iceberg tiers.

## 2. Context and Cross-Plane Interactions

Per [OVR-ARCH-3P-001](../../overview/three-plane-architecture.md) and [OVR-ARCH-XPL-001](../../overview/cross-plane-interactions.md), the Intelligence Plane interacts across Plane boundaries strictly through injected ports and provider-owned contracts:

| Interaction | Direction | Authoritative Contract | `AS-IS` Reality | `TARGET` Intent |
|---|---|---|---|---|
| **On-Demand Run Trigger (`XPL-04`)** | Application (`CAP-APP-AGT-001`) -> Intelligence (`CAP-INT-ORC-001`) | `src/intelligence/workflows/investigation.py` & `CAP-APP-AGT-001` `openapi.yaml` | `PlatformRuntimeContainer.execute_agent_investigation()` awaits `MarketIntelligenceGraph.run_investigation()` **inline synchronously** inside `POST /api/v1/agents/runs` before returning HTTP `202`. | API inserts `QUEUED` row into PostgreSQL `agent_runs` and returns `202` immediately; `agent-worker` polls/executes asynchronously. |
| **Deterministic Tool Data Access (`XPL-05`)** | Intelligence (`CAP-INT-ORC-001`) -> Data Plane (`CAP-DP-STR-002`) & App Runtime | [tool-contracts.yaml](../shared-contracts/tool-contracts.yaml) (`src/intelligence/tools/contracts.py`) | `PlatformRuntimeContainer._register_all_ten_deterministic_tools()` injects 10 Python closures reading in-memory `HotStateProjector` / `ClickHouseBatchSink` and mutating `runtime.reports` / `runtime.detected_anomalies`. | Isolated `agent-worker` binds read-only clients (`fmdp_agent_ro` ClickHouse, Redis) and read-write `fmdp_agent_rw` PostgreSQL persistence for reports/invocations. |
| **Anomaly Event Trigger (`XPL-06`)** | Data Plane (`CAP-DP-STR-002`) -> Intelligence (`CAP-INT-ORC-001`) | Data Plane [asyncapi.yaml](../../data-plane/shared-contracts/asyncapi.yaml) (`market.anomalies.v1`) | **NOT_IMPLEMENTED**: `StatisticalAnomalyDetector` and `POST /analytics/anomalies/evaluate` emit `EventEnvelopeV1` (`ANOMALY`), but zero Intelligence consumer subscribes to `market.anomalies.v1`. | `agent-worker` consumes `market.anomalies.v1` via consumer group and launches `trigger_mode="EVENT_TRIGGERED"` runs with 900s cooldown protection. |

## 3. Building Blocks and Dependency Boundaries

### 3.1 Internal Subsystems (`src/intelligence/`)

| Package / Module | Responsibility | Key Symbols |
|---|---|---|
| `orchestrator/graph.py` | 5-node bounded workflow loop & LLM adapter | `MarketIntelligenceGraph`, `DeterministicMockLLMAdapter` |
| `workflows/investigation.py` | Node registry & mutable run state schema | `WORKFLOW_NODES`, `AgentWorkflowState` |
| `tools/contracts.py` | Approved 10-tool enum, governance policies & provenance wrappers | `ApprovedAgentTool`, `ToolGovernancePolicy`, `APPROVED_TOOL_POLICIES`, `ToolProvenanceMetadata`, `ToolExecutionEnvelope` |
| `tools/gateway.py` | Security/determinism firewall & audit recorder | `ControlledToolGateway`, `UnauthorizedToolAccessError`, `ToolQueryLimitExceededError` |
| `reporting/validator.py` | Citation provenance validation | `ReportValidator`, `ReportProvenanceError` |
| `main.py` | Worker container entrypoint (`AS-IS` logging stub) | `main()` |

### 3.2 Clean Architecture AST Dependency Rules

Verified by [test_clean_architecture_boundaries.py](../../../tests/architecture/test_clean_architecture_boundaries.py):

- **Allowed Upstream Dependencies**: `src/intelligence/` may import Python standard library, optional `src/shared/` primitives, and its own internal subpackages (`src.intelligence.*`).
- **Prohibited Imports**: `src/intelligence/` MUST NEVER import `src.ingestion`, `src.streaming`, `src.lakehouse`, or `src.serving`.
- **Reverse Isolation**: Neither `src/shared/`, `src/ingestion/`, `src/streaming/`, `src/lakehouse/{bronze,silver,gold,quality,catalog}/`, nor `src/serving/api/` may import `src.intelligence`.
- **Composition Root**: Only `src/serving/infrastructure/runtime.py` (`PlatformRuntimeContainer`) wires `ControlledToolGateway` closures and `MarketIntelligenceGraph` across Planes `AS-IS`.

## 4. Runtime Topology (`AS-IS` vs `TARGET`)

| Dimension | `AS-IS` Observed Reality | `TARGET` Architecture |
|---|---|---|
| **Process Hosting** | Runs inside FastAPI `backend-api` (`:8000`) or `svc-intelligence-agent` (`:8006`) via `PlatformRuntimeContainer`. `agent-worker` (`src/intelligence/main.py`) logs 1 line and exits immediately. | `agent-worker` runs as an independent container (`docker-compose.yml --profile intelligence`), isolated from HTTP serving latency and ingestion spikes. |
| **Graph Engine** | Pure Python `while` loop (`graph.py:131-155`); zero `langgraph` imports in `src/intelligence/`. | Stateful `langgraph` `StateGraph` (`pyproject.toml` optional extra `intelligence`) with checkpoint persistence. |
| **LLM Provider** | `DeterministicMockLLMAdapter` (`LLM_PROVIDER=mock` in `.env.example`, though `settings.py` does not load `LLM_*` vars). | Pluggable external LLM adapter (`LLM_PROVIDER`, `LLM_MODEL_NAME`, `LLM_API_KEY`) behind explicit prompt/budget/timeout boundaries. |
| **Persistence** | Ephemeral Python dicts (`runtime.agent_runs`, `runtime.reports`, `gateway._audit_log`). `deploy/postgres/init/01_schema.sql` (`agent_runs`, `agent_tool_invocations`) is unwired. | PostgreSQL 16 (`fmdp_agent_rw`) persists queued/running/completed states, tool invocation records, token usage, and structured reports. |

## 5. Architectural Gaps and Technical Risks

| Gap ID | Category | Verified Evidence & Impact | Status |
|---|---|---|---|
| `GAP-INT-001` | **No Async Worker Isolation** | `src/intelligence/main.py` exits immediately; `POST /api/v1/agents/runs` blocks HTTP response on full execution (`agent_api/router.py:56`). | `OPEN` |
| `GAP-INT-002` | **No LangGraph / Postgres Checkpointing** | Zero `langgraph` imports or `asyncpg`/`sqlalchemy` queries; runs and reports vanish on container restart and cannot share state with `svc-intelligence-agent` (`:8006`). | `OPEN` |
| `GAP-INT-003` | **Mock LLM Only & Unwired `LLM_*` Config** | `DeterministicMockLLMAdapter` executes hardcoded 7-tool plan regardless of `prompt_summary`; `LLM_PROVIDER`/`LLM_MODEL_NAME`/`LLM_API_KEY`/`AGENT_RUN_TIMEOUT_SECONDS` are absent from `PlatformConfig`. | `OPEN` |
| `GAP-INT-004` | **Hardcoded Internal Agent Permissions** | `MarketIntelligenceGraph` hardcodes `self._agent_permissions` (`graph.py:117`) ignoring caller JWT role; HTTP trigger route has no `Depends` auth guard (`SEC-AUDIT-003`). | `BLOCKED` |
| `GAP-INT-005` | **Undeclared Tool Write Side Effects** | `generate_analysis_report` mutates `runtime.reports` and `detect_anomalies` mutates `anomaly_detector._cooldown_registry` + `runtime.detected_anomalies` despite `is_read_only_market_data=True` default. | `OPEN` |
| `GAP-INT-006` | **Unimplemented Event-Triggered Consumer** | No Kafka consumer reads `market.anomalies.v1`; `EVENT_TRIGGERED` only works if manually passed in `POST /api/v1/agents/runs` JSON body. | `OPEN` |
| `GAP-INT-007` | **Static Monitored Symbol List Drift** | `MarketIntelligenceGraph` receives `monitored_symbols` snapshot at container `__init__`; instruments later added via `PUT /api/v1/catalog/instruments` are still rejected by Node 1. | `OPEN` |
