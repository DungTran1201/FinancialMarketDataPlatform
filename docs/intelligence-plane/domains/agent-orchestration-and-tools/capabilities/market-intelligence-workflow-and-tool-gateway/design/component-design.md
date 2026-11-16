---
doc_id: CAP-INT-ORC-COMP-001
title: "Component Design: Market Intelligence Workflow & Tool Gateway"
doc_type: architecture
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
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-AGENT-001
  - INT-ARCH-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Authored capability component design for all 6 modules in src/intelligence/."
---

# Component Design: `CAP-INT-ORC-001`

## 1. Internal Module Decomposition

| Module | Primary Classes / Symbols | Responsibility |
|---|---|---|
| `src/intelligence/orchestrator/graph.py` | `MarketIntelligenceGraph`, `DeterministicMockLLMAdapter` | Drives 5-node workflow loop and mock planner/synthesizer. |
| `src/intelligence/workflows/investigation.py` | `WORKFLOW_NODES`, `AgentWorkflowState` | Defines canonical node names and `can_continue_planning()` guard. |
| `src/intelligence/tools/contracts.py` | `ApprovedAgentTool`, `ToolGovernancePolicy`, `APPROVED_TOOL_POLICIES`, `ToolProvenanceMetadata`, `ToolExecutionEnvelope` | Declares 10-tool enum, policies, and immutable provenance envelopes. |
| `src/intelligence/tools/gateway.py` | `ControlledToolGateway`, `UnauthorizedToolAccessError`, `ToolQueryLimitExceededError` | Enforces whitelist, RBAC, row cap, `asyncio.wait_for`, and `_audit_log`. |
| `src/intelligence/reporting/validator.py` | `ReportValidator`, `ReportProvenanceError` | Verifies non-empty citations and `invocation_id` membership. |
| `src/intelligence/main.py` | `main()` | `agent-worker` CLI entrypoint (stub: logs config and exits). |

## 2. Composition Root Wiring (`src/serving/infrastructure/runtime.py`)

`PlatformRuntimeContainer` instantiates `ControlledToolGateway()`, registers all 10 async closures in `_register_all_ten_deterministic_tools()`, and constructs `MarketIntelligenceGraph(tool_gateway=self.tool_gateway)`.

