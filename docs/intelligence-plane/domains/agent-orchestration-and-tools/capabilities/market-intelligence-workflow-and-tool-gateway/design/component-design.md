---
doc_id: CAP-INT-ORC-COMP-001
title: "Component & Interface Design: Market Intelligence Workflow & Tool Gateway"
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
    - "src/intelligence/main.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-REQ-001
  - CAP-INT-ORC-AGT-001
  - CAP-INT-ORC-ERR-001
  - DIAG-INT-DEP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented internal module decomposition, port wiring via PlatformRuntimeContainer, and state/error interfaces."
---

# Component & Interface Design: Market Intelligence Workflow & Tool Gateway

## 1. Module Decomposition (`src/intelligence/`)

| Module | Primary Symbols | Responsibilities & Design Constraints |
|---|---|---|
| `orchestrator/graph.py` | `DeterministicMockLLMAdapter`, `MarketIntelligenceGraph` | Executes 5-node async loop (`run_investigation`); delegates all tool calls to `ControlledToolGateway` and validation to `ReportValidator`. |
| `workflows/investigation.py` | `WORKFLOW_NODES`, `AgentWorkflowState` | Holds run state, iteration/token counters, and `can_continue_planning()` loop guard. |
| `tools/contracts.py` | `ApprovedAgentTool`, `ToolGovernancePolicy`, `APPROVED_TOOL_POLICIES`, `ToolProvenanceMetadata`, `ToolExecutionEnvelope` | Immutable tool catalog and provenance contracts; no IO or runtime dependencies. |
| `tools/gateway.py` | `ControlledToolGateway`, `UnauthorizedToolAccessError`, `ToolQueryLimitExceededError` | Mediates tool dispatch (`execute_tool`), checks whitelist/RBAC/bounds, enforces `asyncio.wait_for`, builds UUIDv4 provenance, records `_audit_log`. |
| `reporting/validator.py` | `ReportValidator`, `ReportProvenanceError` | Static verifier ensuring non-empty citations referencing valid `invocation_id`s in `evidence_trail`. |
| `main.py` | `main()` | Standalone worker bootstrap (`AS-IS` stub logging `PlatformConfig` and exiting). |

## 2. Composition & Interface Wiring (`PlatformRuntimeContainer`)

In `src/serving/infrastructure/runtime.py:170-176` & `401-597`:

- **Handler Injection**: `_register_all_ten_deterministic_tools()` binds 10 async Python closures over `latest_price_handler`, `hot_redis_projector`, `clickhouse_sink`, `anomaly_detector`, `self.detected_anomalies`, and `self.reports` into `ControlledToolGateway`.
- **Execution Entrypoint**: `execute_agent_investigation()` enforces `idempotency_keys`, inserts `AgentWorkflowState` into `self.agent_runs`, awaits `self.intelligence_graph.run_investigation(state)`, and returns `(AgentRunTicket, AgentWorkflowState)` to `CAP-APP-AGT-001`.
- **Clean Architecture Boundary**: `src/intelligence/` never imports `src/serving/` or `src/streaming/`; dependency inversion occurs exclusively inside `PlatformRuntimeContainer`.

## 3. Error Handling & Boundary Gaps (`AS-IS`)

1. `MarketIntelligenceGraph.run_investigation()` lacks `try/except` around Nodes 2–5: any `UnauthorizedToolAccessError`, `ToolQueryLimitExceededError`, `asyncio.TimeoutError`, `ReportProvenanceError`, or handler `ValueError` escapes unhandled and leaves `state.status == "RUNNING"`.
2. `ControlledToolGateway` returns `{"status": "stub_ok", ...}` instead of raising an error when no handler is registered for an `ApprovedAgentTool`.
3. Detailed exception catalog lives in [error-catalog.md](../contracts/error-catalog.md).

