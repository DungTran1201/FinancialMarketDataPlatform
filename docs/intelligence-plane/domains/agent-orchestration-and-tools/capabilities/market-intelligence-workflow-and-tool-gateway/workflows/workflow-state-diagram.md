---
doc_id: DIAG-INT-ORC-STATE-001
title: "Agent Workflow State Diagram"
doc_type: diagram
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
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/architecture/agent-runtime-architecture.md"
    - "src/intelligence/workflows/investigation.py"
related_docs:
  - INT-ARCH-RT-001
  - CAP-INT-ORC-UC-005
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created Workflow State Machine diagram showing AS-IS transitions and TARGET CANCELLED/error recovery states."
---

# Agent Workflow State Diagram

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-STATE-001` |
| **Purpose** | Model `AgentWorkflowState.status` lifecycle transitions (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `TARGET CANCELLED`). |
| **Scope & Owner** | `capability` (`CAP-INT-ORC-001`) / `ai-engineer` |
| **Authoritative Source** | [agent-runtime-architecture.md](../../../../../architecture/agent-runtime-architecture.md) (`INT-ARCH-RT-001`) |
| **Notation** | Mermaid `stateDiagram-v2` (UML 2.5.1 State Machine) |
| **Version & Status** | `2.0.0` / `DRAFT` (`SIMULATED`) |

```mermaid
stateDiagram-v2
    [*] --> QUEUED : "AgentWorkflowState initialized"
    QUEUED --> FAILED : "Node 1 symbol not in _monitored_symbols"
    QUEUED --> RUNNING : "Node 1 symbol validated"
    RUNNING --> COMPLETED : "Node 5 ReportValidator & generate_analysis_report succeed"
    RUNNING --> FAILED : "TARGET catch tool/validator exceptions (uncaught AS-IS)"
    QUEUED --> CANCELLED : "TARGET Postgres DDL status"
    RUNNING --> CANCELLED : "TARGET Postgres DDL status"
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]
```

**Legend**: `QUEUED`, `RUNNING`, `COMPLETED`, and Node 1 `FAILED` are implemented `AS-IS`; `CANCELLED` (from `01_schema.sql`) and Node 3/5 `FAILED` catch are `TARGET`.
