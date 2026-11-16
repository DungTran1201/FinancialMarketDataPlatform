---
doc_id: DIAG-APP-AGT-SEQ-001
title: "Sequence Diagram: Agent Investigation Trigger, Replay & Report Fetch"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: agent-experience-and-reporting
capability_id: CAP-APP-AGT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/agent-experience-and-reporting/capabilities/agent-run-and-report-portal/use-cases/uc-agt-001-trigger-and-stream-agent-run.md"
related_docs:
  - CAP-APP-AGT-UC-001
  - CAP-APP-AGT-UC-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Rendered cross-plane invocation sequence from AiWorkspaceModule through Application routers into Intelligence Plane."
---

# Sequence Diagram: Agent Investigation Trigger, Replay & Report Fetch

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-AGT-SEQ-001` |
| **Title & Purpose** | Portal `POST /agents/runs`, Cross-Plane Execution, SSE Replay & `GET /reports/{run_id}` |
| **Owner Role & Scope** | `fullstack-engineer / CAP-APP-AGT-001` |
| **Authoritative Source** | [uc-agt-001-trigger-and-stream-agent-run.md](../use-cases/uc-agt-001-trigger-and-stream-agent-run.md) (`CAP-APP-AGT-UC-001`) |
| **Notation** | `Mermaid sequenceDiagram` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
sequenceDiagram
    autonumber
    participant UI as AiWorkspaceModule
    participant API as Agent/Reporting Routers
    participant RT as PlatformRuntimeContainer
    participant WF as Intelligence Workflow (CAP-INT-ORC-001)

    UI->>API: POST /api/v1/agents/runs (Idempotency-Key)
    API->>RT: execute_agent_investigation(...)
    RT->>WF: Run 5-node workflow inline (AS-IS synchronous)
    WF-->>RT: Complete AgentWorkflowState + Structured Report
    API-->>UI: 202 {run_id, status, tool_calls_executed}
    UI->>API: GET /api/v1/agents/runs/{run_id}/events
    API-->>UI: SSE replay: tool_invocation* + run_completed
    UI->>API: GET /api/v1/reports/{run_id}
    API-->>UI: 200 Verified report + provenance_citations
```

## 3. Legend

- **Inline Synchronous Await**: Step 3 completes entire investigation before HTTP `202` is sent; Step 6 replays stored `evidence_trail`.
