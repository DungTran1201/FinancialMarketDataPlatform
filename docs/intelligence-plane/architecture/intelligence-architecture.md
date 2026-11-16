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
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
    - "src/intelligence/main.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-RT-001
  - INT-ARCH-LLM-001
  - INT-ARCH-GW-001
  - INT-ARCH-SEC-001
  - INT-ARCH-EVAL-001
  - DIAG-INT-C4-001
  - DIAG-INT-DEP-001
  - ADR-INT-0001
  - OVR-ARCH-XPL-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Expanded Intelligence Plane architecture covering context, ownership, building blocks, dependency DAG, cross-plane interactions, AS-IS vs TARGET topology, and verified gaps."
---

# Intelligence Plane Architecture Description

Derived diagrams: [intelligence-c4-container.md](diagrams/intelligence-c4-container.md) (`DIAG-INT-C4-001`) and [intelligence-dependency-diagram.md](diagrams/intelligence-dependency-diagram.md) (`DIAG-INT-DEP-001`).

## 1. Context, Scope & Ownership

The **Intelligence Plane (Plane C)** is responsible for synthesizing structured, citation-grounded quantitative market investigation reports without granting any LLM direct SQL, network, or arbitrary code execution access ([ADR-OVR-003](../../overview/architecture/decisions/adr-0003-decimal-precision-and-deterministic-tool-gateway.md), [ADR-INT-0001](decisions/adr-0001-deterministic-gateway-over-freeform-sql.md)).

### Ownership Split
- **Owned by Intelligence Plane (`src/intelligence/`, `CAP-INT-ORC-001`)**:
  - 5-node investigation workflow (`MarketIntelligenceGraph`, `AgentWorkflowState`).
  - Model adapter abstraction (`DeterministicMockLLMAdapter` `AS-IS`; external LLM adapters `TARGET`).
  - Controlled Tool Registry & Gateway (`ApprovedAgentTool`, `APPROVED_TOOL_POLICIES`, `ControlledToolGateway`).
  - Evidence trail (`ToolExecutionEnvelope`, `ToolProvenanceMetadata`) & citation validation (`ReportValidator`).
- **Owned by Other Planes (Referenced Only)**:
  - **Application Plane (`CAP-APP-AGT-001`)**: HTTP API (`POST /api/v1/agents/runs`, `GET /api/v1/reports/{run_id}`), auth/IAM, `AiWorkspaceModule` UI, and `PlatformRuntimeContainer` handler wiring.
  - **Data Plane (`CAP-DP-STR-002`)**: Redis hot cache, ClickHouse OLAP, anomaly detector, and `market.anomalies.v1` Kafka contract.

## 2. Building Blocks

| Component | Module (`src/intelligence/`) | Responsibility | `AS-IS` Implementation |
|---|---|---|---|
| **Orchestrator** | `orchestrator/graph.py` | `MarketIntelligenceGraph` & `DeterministicMockLLMAdapter` | Pure Python `while` loop; mock planner & synthesizer. |
| **Workflow State** | `workflows/investigation.py` | `WORKFLOW_NODES` (5 nodes) & `AgentWorkflowState` | In-memory dataclass; `can_continue_planning()` loop guard. |
| **Tool Contracts** | `tools/contracts.py` | `ApprovedAgentTool` (10 tools), `APPROVED_TOOL_POLICIES`, envelopes | Static enum + policy dict; `GENERATE_ANALYSIS_REPORT` defaults `is_read_only_market_data=True`. |
| **Tool Gateway** | `tools/gateway.py` | `ControlledToolGateway` whitelist, RBAC, row cap, `asyncio.wait_for`, `_audit_log` | Enforces checks; falls back to `stub_ok` if handler unregistered. |
| **Report Validator** | `reporting/validator.py` | `ReportValidator.validate_report()` | Verifies non-empty `provenance_citations` and `invocation_id` membership. |
| **Worker Entrypoint** | `main.py` | `agent-worker` process bootstrap (`--profile intelligence`) | Logs config and exits immediately; no queue polling. |

## 3. Dependency Boundaries

Enforced by AST tests in [test_clean_architecture_boundaries.py](../../../tests/architecture/test_clean_architecture_boundaries.py):
- `src/intelligence/` MAY import only from `src/shared/` and Python stdlib/declared libraries.
- `src/intelligence/` MUST NEVER import `src/ingestion/`, `src/streaming/`, `src/lakehouse/`, or `src/serving/`.
- Concrete Data Plane and Application Plane store bindings are injected **into** `ControlledToolGateway` by `PlatformRuntimeContainer` (`src/serving/infrastructure/runtime.py`) via async closures.

## 4. Cross-Plane Interactions

- **Application Plane -> Intelligence Plane (`CAP-APP-AGT-001 -> CAP-INT-ORC-001`, `XPL-04`)**: FastAPI router invokes `await runtime.execute_agent_investigation(...)` synchronously inside `POST /api/v1/agents/runs` (`202` response is returned after workflow completion `AS-IS`).
- **Intelligence Plane -> Data Plane / App Runtime (`XPL-05`)**: `ControlledToolGateway` invokes injected closures reading `HotStateProjector`, `ClickHouseBatchSink`, `AnomalyDetector`, and mutating `runtime.reports` / `runtime.detected_anomalies`.
- **Data Plane -> Intelligence Plane (`XPL-06`, `TARGET`)**: `market.anomalies.v1` Kafka topic is defined in Data Plane, but no Kafka consumer in `src/intelligence/` subscribes to it (`NOT_IMPLEMENTED`).

## 5. Runtime Topology (`AS-IS` vs `TARGET`)

| Dimension | `AS-IS` Runtime Reality | `TARGET` Architecture |
|---|---|---|
| **Process Model** | Runs inline inside `fmdp-backend-api` (`PlatformRuntimeContainer`) | Isolated `fmdp-agent-worker` (`--profile intelligence`) polling job queue |
| **Workflow Engine** | Pure Python `while` loop (`zero` `langgraph` imports) | Stateful LangGraph execution with checkpointing (`langgraph>=0.1.0` optional extra) |
| **LLM Provider** | `DeterministicMockLLMAdapter` (`420` + `540` fixed tokens) | Pluggable external LLM adapter with circuit breaker & timeout |
| **State & Report Storage** | In-memory Python dicts (`runtime.agent_runs`, `runtime.reports`) | Durable PostgreSQL `agent_runs` and `agent_tool_invocations` (`01_schema.sql`) |
| **Trigger Modes** | `ON_DEMAND` HTTP only (even if `trigger_mode="EVENT_TRIGGERED"` is passed) | `ON_DEMAND` async queue + `EVENT_TRIGGERED` Kafka consumer on `market.anomalies.v1` |

## 6. Architectural Gaps & Technical Risks

1. **`GAP-INT-001` (Inline Execution)**: `POST /api/v1/agents/runs` awaits the entire workflow before returning HTTP `202`.
2. **`GAP-INT-002` (Stubbed Worker & No Queue)**: `src/intelligence/main.py` exits immediately; `agent-worker` container in `docker-compose.yml` does not poll PostgreSQL or Kafka.
3. **`GAP-INT-003` (In-Memory State Loss)**: Restarting `backend-api` loses all `agent_runs`, `reports`, `idempotency_keys`, and `ControlledToolGateway._audit_log`.
4. **`GAP-INT-004` (Hardcoded Permissions & Symbols)**: `MarketIntelligenceGraph` hardcodes `_agent_permissions` and 5 monitored symbols (`BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, `XRPUSDT`) instead of reading caller RBAC or catalog.
5. **`GAP-INT-005` (Hidden Tool Side Effects)**: `generate_analysis_report` mutates `runtime.reports` and `detect_anomalies` appends to `runtime.detected_anomalies` while `ToolGovernancePolicy.is_read_only_market_data` defaults to `True`.
6. **`GAP-INT-006` (Shallow Hallucination Check)**: `ReportValidator` only checks `invocation_id` existence, not numeric equivalence between narrative text and tool outputs.
