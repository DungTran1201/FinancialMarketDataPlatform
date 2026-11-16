---
doc_id: INT-DOM-ORC-SPEC-001
title: "Domain Specification: Agent Orchestration & Tools"
doc_type: specification
plane: intelligence-plane
scope_level: domain
domain: agent-orchestration-and-tools
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
  - INT-DOM-ORC-001
  - INT-ARCH-001
  - CAP-INT-ORC-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Defined bounded context, domain concepts, owned components, and dependency boundaries for agent-orchestration-and-tools."
---

# Domain Specification: Agent Orchestration & Tools

## 1. Bounded Context & Responsibilities

The `agent-orchestration-and-tools` domain encapsulates all autonomous market investigation orchestration, model planning/synthesis adapters, deterministic tool mediation, and citation provenance verification inside the **Intelligence Plane**.

- **Owned Components**: `MarketIntelligenceGraph`, `DeterministicMockLLMAdapter`, `AgentWorkflowState`, `WORKFLOW_NODES`, `ApprovedAgentTool`, `APPROVED_TOOL_POLICIES`, `ControlledToolGateway`, `ToolExecutionEnvelope`, `ToolProvenanceMetadata`, `ReportValidator`, `agent-worker` (`main.py`).
- **Out of Bounded Context**: HTTP routing (`/api/v1/agents`, `/api/v1/reports`), user JWT/RBAC management, frontend `AiWorkspaceModule`, and Data Plane market storage engines.

## 2. Ubiquitous Domain Concepts

| Concept | Definition | Code Artifact |
|---|---|---|
| **Investigation Run** | Stateful 5-node analytical execution for a target `symbol` with iteration & token budgets | `AgentWorkflowState` |
| **Approved Agent Tool** | Enumerated deterministic tool contract with permission, row cap, and timeout | `ApprovedAgentTool` |
| **Tool Execution Envelope** | Standardized wrapper pairing tool output `data` with immutable `ToolProvenanceMetadata` | `ToolExecutionEnvelope` |
| **Provenance Citation** | Verifiable reference linking a report back to a specific `invocation_id` in `evidence_trail` | `ReportValidator` |

## 3. Dependency Boundaries

- **Upstream Consumers**: Application Plane (`CAP-APP-AGT-001`) triggers investigations via `PlatformRuntimeContainer.execute_agent_investigation()`.
- **Injected Dependencies**: Concrete Data Plane / Application Runtime handlers are registered into `ControlledToolGateway` by `PlatformRuntimeContainer` without any direct Python imports from `src/serving/` or `src/streaming/`.

