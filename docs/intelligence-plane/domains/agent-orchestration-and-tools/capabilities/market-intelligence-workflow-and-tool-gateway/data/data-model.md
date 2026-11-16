---
doc_id: CAP-INT-ORC-DM-001
title: "Logical Data Model: Agent State, Tool Provenance & Reports"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: database-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/workflows/investigation.py"
    - "src/intelligence/tools/contracts.py"
    - "src/serving/api/modules/reporting/domain/ports.py"
    - "deploy/postgres/init/01_schema.sql"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-DB-001
  - DIAG-INT-ORC-ERD-001
  - APP-ARCH-DATA-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Defined logical entities, keys, invariants, and structural drift between runtime dataclasses and Postgres DDL."
---

# Logical Data Model: Agent State, Tool Provenance & Reports

Authoritative contract reference: [data-contract.yaml](../../../../../shared-contracts/data-contract.yaml). Physical DDL design: [database-design.md](database-design.md). Derived ERD: [agent-state-erd.md](agent-state-erd.md) (`DIAG-INT-ORC-ERD-001`).

## 1. Conceptual & Logical Entities

| Entity | Code / DDL Representation | Primary Key | Cardinality & Relationships | Temporal & Numeric Rules |
|---|---|---|---|---|
| **AgentRun** | `AgentWorkflowState` (`investigation.py`) / `agent_runs` (`01_schema.sql`) | `run_id` (`run_<hex12>` `AS-IS`; `UUID` in DDL) | `1` AgentRun -> `0..N` `ToolInvocation` (`evidence_trail`); `1` AgentRun -> `0..1` `StructuredAnalysisReport`; `0..1` optional FK to `users(id)` (`requested_by`). | Timestamps UTC (`TIMESTAMPTZ`); financial prices in reports stored as strings/JSON (`Decimal`-serialized in upstream tools). |
| **ToolInvocation** | `ToolExecutionEnvelope` + `ToolProvenanceMetadata` (`contracts.py`) / `agent_tool_invocations` (`01_schema.sql`) | `invocation_id` (`UUIDv4`) | `N` invocations belong to `1` `AgentRun` (`ON DELETE CASCADE`). | `executed_at`, `window_start`, `window_end` UTC; `row_count >= 0`. |
| **StructuredAnalysisReport** | `StructuredAnalysisReport` (`reporting/domain/ports.py`) / `agent_runs.structured_report` (`JSONB`) | `run_id` | Embedded in `AgentWorkflowState.final_report` and stored in `runtime.reports[run_id]`; contains `1..N` `ProvenanceCitation` references linking back to `ToolInvocation.invocation_id`. | Report timestamps ISO-8601 UTC. |
| **IdempotencyIndex** | `PlatformRuntimeContainer.idempotency_keys` (`dict[str, str]`) | `idempotency_key` | Maps client `Idempotency-Key` header -> `1` `AgentRun.run_id`. | Missing from `01_schema.sql` (`OPEN-INT-004`). |

## 2. Structural Drift & Invariants (`AS-IS` vs `TARGET`)

1. **Primary Key Type Mismatch**: `PlatformRuntimeContainer` creates `run_id = f"run_{uuid.uuid4().hex[:12]}"`, which fails PostgreSQL `UUID` column validation in `agent_runs.run_id`.
2. **State Machine Enum Drift**: `AgentWorkflowState.status` allows `QUEUED | RUNNING | COMPLETED | FAILED`; Postgres `agent_runs` adds `CANCELLED`.
3. **Invocation Status Drift**: `ToolExecutionEnvelope.status` comment lists `SUCCESS | TIMEOUT | VALIDATION_ERROR | PERMISSION_DENIED`; Postgres `agent_tool_invocations` CHECK lists `'SUCCESS' | 'TIMEOUT' | 'VALIDATION_ERROR' | 'SOURCE_ERROR'`.
4. **Missing Columns in DDL**: `01_schema.sql` lacks `idempotency_key`, `visited_nodes`, `current_iteration`, and `max_iterations` needed for worker resume/checkpoints.
