---
doc_id: DIAG-INT-ORC-ERD-001
title: "ERD: Agent Runs, Tool Invocations & Structured Reports"
doc_type: diagram
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: NOT_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/data/data-model.md"
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/data/database-design.md"
related_docs:
  - CAP-INT-ORC-DM-001
  - CAP-INT-ORC-DB-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Rendered Crow's Foot ERD matching deploy/postgres/init/01_schema.sql and runtime state objects."
---

# ERD: Agent Runs, Tool Invocations & Structured Reports

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-ERD-001` |
| **Title & Purpose** | Entity-Relationship view of `users` (ref), `agent_runs`, `agent_tool_invocations`, and logical `StructuredAnalysisReport` |
| **Owner Role & Scope** | `database-architect / CAP-INT-ORC-001` |
| **Authoritative Source** | [data-model.md](data-model.md) (`CAP-INT-ORC-DM-001`) & [database-design.md](database-design.md) (`CAP-INT-ORC-DB-001`) |
| **Notation** | `Mermaid erDiagram` (`Crow's Foot`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
erDiagram
    USERS {
        uuid id PK "Owned by CAP-APP-IAM-001"
        varchar email UK
        varchar role
    }

    AGENT_RUNS {
        uuid run_id PK "AS-IS runtime uses run_hex12 in memory"
        varchar trigger_mode "ON_DEMAND | EVENT_TRIGGERED"
        uuid requested_by FK "Nullable user reference"
        varchar symbol "Normalized spot pair"
        varchar status "QUEUED | RUNNING | COMPLETED | FAILED | CANCELLED"
        text prompt_summary
        jsonb structured_report "Nullable JSONB report payload"
        jsonb token_usage "prompt_tokens, completion_tokens, total_tokens"
        timestamptz started_at
        timestamptz completed_at
    }

    AGENT_TOOL_INVOCATIONS {
        uuid invocation_id PK
        uuid run_id FK "ON DELETE CASCADE"
        varchar tool_name "ApprovedAgentTool enum value"
        jsonb input_params
        jsonb output_metadata "Provenance & row counts"
        varchar status "SUCCESS | TIMEOUT | VALIDATION_ERROR | SOURCE_ERROR"
        timestamptz started_at
    }

    PROVENANCE_CITATION {
        uuid invocation_id FK "Logical citation link inside structured_report"
        varchar tool_name
        varchar source_store
        varchar symbol
        timestamptz window_start
        timestamptz window_end
        int row_count
    }

    USERS ||--o{ AGENT_RUNS : "requests (optional FK)"
    AGENT_RUNS ||--o{ AGENT_TOOL_INVOCATIONS : "executes and audits"
    AGENT_RUNS ||--o{ PROVENANCE_CITATION : "embeds in structured_report JSONB"
    AGENT_TOOL_INVOCATIONS ||--o{ PROVENANCE_CITATION : "referenced by invocation_id"
```

## 3. Legend

- **`USERS` (`CAP-APP-IAM-001`)**: Referenced via nullable `requested_by` FK (`01_schema.sql:44`); not owned by Intelligence Plane.
- **`AGENT_RUNS` & `AGENT_TOOL_INVOCATIONS`**: Declared in `deploy/postgres/init/01_schema.sql:41-66`; currently `NOT_IMPLEMENTED` in runtime (stored in Python dicts `AS-IS`).
- **`PROVENANCE_CITATION`**: Embedded inside `structured_report` JSONB (`StructuredAnalysisReport.provenance_citations`) and verified against `evidence_trail` (`AGENT_TOOL_INVOCATIONS`).

