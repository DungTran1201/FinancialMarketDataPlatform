---
doc_id: CAP-INT-ORC-DM-001
title: "Data Model: Intelligence Plane State & Provenance"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/workflows/investigation.py"
    - "src/intelligence/tools/contracts.py"
    - "deploy/postgres/init/01_schema.sql"
related_docs:
  - CAP-INT-ORC-DOC-001
  - DIAG-INT-ORC-ERD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Documented AS-IS in-memory state/envelope structures and TARGET PostgreSQL agent_runs/agent_tool_invocations entities."
---

# Data Model: Intelligence Plane (`CAP-INT-ORC-001`)

Canonical machine-readable contract: [data-contract.yaml](../../../../../shared-contracts/data-contract.yaml). Derived ERD: [agent-state-erd.md](agent-state-erd.md) (`DIAG-INT-ORC-ERD-001`).

## Entities (`AS-IS` Memory vs. `TARGET` PostgreSQL)

- **`AgentWorkflowState` (`agent_runs` TARGET)**: Tracks `run_id` (PK), `trigger_mode`, `symbol`, `status`, `prompt_summary`, `final_report` (`structured_report JSONB`), and `tokens_consumed` (`token_usage JSONB`).
- **`ToolExecutionEnvelope` + `ToolProvenanceMetadata` (`agent_tool_invocations` TARGET)**: Tracks `invocation_id` (PK), `run_id` (FK), `tool_name`, `source_store`, `symbol`, `window_start`, `window_end`, `row_count`, `status`, and `executed_at`.
- **`StructuredAnalysisReport`**: Stored in `runtime.reports[run_id]` (`AS-IS`) and `agent_runs.structured_report` (`TARGET`).
