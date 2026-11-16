---
doc_id: DIAG-INT-ORC-ERD-001
title: "Agent State & Tool Invocation ERD"
doc_type: diagram
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: NOT_IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/data/data-model.md"
    - "deploy/postgres/init/01_schema.sql"
related_docs:
  - CAP-INT-ORC-DM-001
  - CAP-INT-ORC-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Created ERD for TARGET PostgreSQL agent_runs and agent_tool_invocations persistence."
---

# Agent State & Tool Invocation ERD

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-ERD-001` |
| **Purpose** | Visualize the `TARGET` PostgreSQL persistence model (`01_schema.sql`) vs `AS-IS` in-memory `AgentWorkflowState`. |
| **Scope & Owner** | `capability` (`CAP-INT-ORC-001`) / `data-architect` |
| **Authoritative Source** | [data-model.md](data-model.md) (`CAP-INT-ORC-DM-001`) |
| **Notation** | Mermaid `erDiagram` (Crow's Foot) |
| **Version & Status** | `2.0.0` / `DRAFT` (`NOT_IMPLEMENTED` in runtime) |

```mermaid
erDiagram
    AGENT_RUNS {
        uuid run_id PK
        varchar trigger_mode
        uuid requested_by FK
        varchar symbol
        varchar status
        text prompt_summary
        jsonb structured_report
        jsonb token_usage
        timestamptz started_at
        timestamptz completed_at
    }

    AGENT_TOOL_INVOCATIONS {
        uuid invocation_id PK
        uuid run_id FK
        varchar tool_name
        jsonb input_params
        jsonb output_metadata
        varchar status
        timestamptz started_at
    }

    AGENT_RUNS ||--o{ AGENT_TOOL_INVOCATIONS : "records 0..N invocations"
```

**Legend**: Tables reflect `deploy/postgres/init/01_schema.sql` (`TARGET` persistence; `AS-IS` runtime uses in-memory `runtime.agent_runs` and `ControlledToolGateway._audit_log`).

