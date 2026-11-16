---
doc_id: INT-CTR-ROOT-001
title: "Intelligence Plane Shared Contracts"
doc_type: index
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - INT-ROOT-001
  - INT-ARCH-GW-001
  - CAP-INT-ORC-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created Intelligence Plane shared-contracts index for canonical 10-tool contracts and state/report data contracts."
---

# Intelligence Plane Shared Contracts

This directory is the **single authoritative contract home** for Intelligence Plane tools and internal data structures.

- [tool-contracts.yaml](tool-contracts.yaml) — Canonical specification for all 10 `ApprovedAgentTool` contracts, permissions, policy-declared vs actual backing stores, row/timeout caps, side effects, and provenance fields.
- [data-contract.yaml](data-contract.yaml) — Canonical data contract for `AgentWorkflowState`, `ToolExecutionEnvelope`, `StructuredAnalysisReport`, and `TARGET` PostgreSQL `agent_runs` / `agent_tool_invocations` persistence.

