---
doc_id: DIAG-INT-ORC-STATE-001
title: "State Diagram: AgentWorkflowState Lifecycle (AS-IS vs TARGET)"
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
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/workflows/workflow-specification.md"
related_docs:
  - INT-ARCH-RT-001
  - CAP-INT-ORC-WF-001
  - CAP-INT-ORC-UC-005
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Rendered AgentWorkflowState transitions including Node 1 FAILED, unhandled RUNNING crash gap, and TARGET CANCELLED state."
---

# State Diagram: `AgentWorkflowState` Lifecycle (`AS-IS` vs `TARGET`)

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-STATE-001` |
| **Title & Purpose** | Lifecycle transitions for `AgentWorkflowState.status` across `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, and `TARGET` `CANCELLED` |
| **Owner Role & Scope** | `ai-engineer / CAP-INT-ORC-001` |
| **Authoritative Source** | [agent-runtime-architecture.md](../../../../../architecture/agent-runtime-architecture.md) (`INT-ARCH-RT-001`) |
| **Notation** | `Mermaid stateDiagram-v2` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
stateDiagram-v2
    [*] --> QUEUED : AgentWorkflowState initialized
    QUEUED --> RUNNING : Node 1 symbol in _monitored_symbols
    QUEUED --> FAILED : Node 1 unmonitored symbol rejected

    RUNNING --> RUNNING : Nodes 2-4 loop while can_continue_planning()
    RUNNING --> COMPLETED : Node 5 ReportValidator & Tool #10 succeed
    RUNNING --> FAILED : TARGET exception/timeout recovery (AS-IS unhandled crash!)
    QUEUED --> CANCELLED : TARGET cancellation before worker pickup
    RUNNING --> CANCELLED : TARGET cooperative abort (not implemented)

    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]
```

## 3. Legend

- **`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`**: Active states used in `src/intelligence/workflows/investigation.py`.
- **`RUNNING -> FAILED` & `CANCELLED`**: Defined in PostgreSQL `agent_runs` CHECK constraint (`01_schema.sql`), but `CANCELLED` and exception-caught `RUNNING -> FAILED` transitions are `NOT_IMPLEMENTED` in `MarketIntelligenceGraph` `AS-IS`.
