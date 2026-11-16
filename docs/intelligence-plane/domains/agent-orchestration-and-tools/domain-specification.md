---
doc_id: INT-DOM-ORC-SPEC-001
title: "Domain Specification: Agent Orchestration & Deterministic Tools"
doc_type: specification
plane: intelligence-plane
scope_level: domain
domain: agent-orchestration-and-tools
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
related_docs:
  - INT-DOM-ORC-001
  - INT-DOM-ORC-GLOSS-001
  - CAP-INT-ORC-DOC-001
  - APP-DOM-AGT-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Defined bounded context, domain concepts, component ownership, and cross-plane boundaries for agent-orchestration-and-tools."
---

# Domain Specification: Agent Orchestration & Deterministic Tools

## 1. Bounded Context & Domain Responsibilities

The **`agent-orchestration-and-tools`** bounded context converts an investigation trigger (`symbol`, `prompt_summary`, `trigger_mode`) into an auditable, citation-backed `StructuredAnalysisReport` using strictly bounded execution loops and deterministic Python/store tools.

### 1.1 Owned Responsibilities

1. **Workflow State & Execution Control**: `WORKFLOW_NODES` (5 nodes), `AgentWorkflowState`, iteration caps (`max_iterations=6`), and planning token ceilings (`80%` of `token_budget=8000`).
2. **Model Adapter Abstraction**: Planning and narrative synthesis (`DeterministicMockLLMAdapter` `AS-IS`; external LLM adapters `TARGET`).
3. **Controlled Tool Mediation**: Whitelisted `ApprovedAgentTool` registry (10 tools), `ToolGovernancePolicy`, RBAC checking, row/period caps, timeout enforcement, and `ToolProvenanceMetadata` attachment.
4. **Provenance Verification & Report Output**: `ReportValidator` checks that report citations match actual `invocation_id`s in `evidence_trail`.

### 1.2 Excluded Responsibilities (Delegated via Cross-Plane Contracts)

- **HTTP Endpoints, AuthN/JWT Issuance & UI (`CAP-APP-AGT-001`, `CAP-APP-IAM-001`)**: Owned by Application Plane (`src/serving/api/modules/{agent_api,reporting,iam}/`, `frontend/`).
- **Market Ingestion, Anomaly Emission & Storage (`CAP-DP-ING-001`, `CAP-DP-STR-001`, `CAP-DP-STR-002`)**: Owned by Data Plane (`src/ingestion/`, `src/streaming/`, `src/lakehouse/`).

## 2. Core Domain Concepts & Owned Components

| Concept / Component | Authoritative Symbol (`src/intelligence/`) | Role in Bounded Context |
|---|---|---|
| **Investigation Graph** | `MarketIntelligenceGraph` (`orchestrator/graph.py`) | Coordinates Nodes 1 -> 2 -> 3 -> 4 -> 5 sequentially with loop budget checks. |
| **Workflow State** | `AgentWorkflowState` (`workflows/investigation.py`) | Captures run status, node trace, token count, planned tools, evidence trail, and final report. |
| **Tool Policy & Envelope** | `ApprovedAgentTool`, `ToolGovernancePolicy`, `ToolExecutionEnvelope` (`tools/contracts.py`) | Defines allowed tools, permissions, bounds, timeouts, and provenance metadata. |
| **Tool Gateway** | `ControlledToolGateway` (`tools/gateway.py`) | Mediates tool calls, checks whitelist/RBAC/limits, enforces timeout, and records audit log. |
| **Report Validator** | `ReportValidator` (`reporting/validator.py`) | Prevents uncited or fabricated `invocation_id` reports (`ReportProvenanceError`). |
| **Worker Entrypoint** | `main()` (`main.py`) | Isolated process bootstrap (`AS-IS`: logs configuration and exits immediately). |

## 3. Dependency & Composition Boundaries

- `src/intelligence/` MUST depend only on `src/shared/` and Python stdlib (`test_clean_architecture_boundaries.py`).
- Concrete Data Plane and Application Runtime handlers are injected exclusively at the composition root (`PlatformRuntimeContainer` in `src/serving/infrastructure/runtime.py` `AS-IS`).

