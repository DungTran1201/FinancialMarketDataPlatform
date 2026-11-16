---
doc_id: DIAG-APP-AGT-STATE-001
title: "State Machine Diagram: Portal-Observed Agent Run Lifecycle"
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
    - "docs/application-plane/domains/agent-experience-and-reporting/capabilities/agent-run-and-report-portal/requirements/capability-specification.md"
related_docs:
  - CAP-APP-AGT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Rendered API/UI run state transitions contrasting QUEUED ticket vs synchronous AS-IS completion."
---

# State Machine Diagram: Portal-Observed Agent Run Lifecycle

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-AGT-STATE-001` |
| **Title & Purpose** | Portal Run Ticket & Outcome Visibility States (`GET /agents/runs/{run_id}`) |
| **Owner Role & Scope** | `fullstack-engineer / CAP-APP-AGT-001` |
| **Authoritative Source** | [capability-specification.md](../requirements/capability-specification.md) (`CAP-APP-AGT-REQ-001`) |
| **Notation** | `Mermaid stateDiagram-v2` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
stateDiagram-v2
    [*] --> AcceptedRun : "POST /agents/runs"
    AcceptedRun --> COMPLETED : "AS-IS inline completion (report stored if validator passed)"
    AcceptedRun --> FAILED : "Guardrail / Tool / Validator rejection"
    COMPLETED --> EvictedOnRestart : "Process restart wipes memory dict"
    FAILED --> EvictedOnRestart : "Process restart wipes memory dict"
    COMPLETED --> [*]
    FAILED --> [*]
    EvictedOnRestart --> [*]
```

## 3. Legend

- **Target `QUEUED -> RUNNING`**: Declared in `deploy/postgres/init/01_schema.sql` CHECK constraint but skipped `AS-IS` because execution finishes synchronously before HTTP `202` response.
