---
doc_id: TPL-REQ-WF-001
title: "Template: Workflow Specification"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: system-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/product-and-requirements/workflow-specification.template.md"
related_docs:
  - GOV-STD-DIAG-001
  - GOV-STD-REQ-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Workflow Specification template aligned with BPMN 2.0.2 and asynchronous/event-driven handoffs."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Initial V2 Workflow Specification template."
---

# Template: Workflow Specification

Used inside `<capability>/workflows/` for multi-step business processes, ingestion/backfill lifecycles, or Agent execution graphs.

---

# Workflow Specification: `<Workflow Name>` (`<WF-DOM-NNN>`)

## 1. Workflow Scope & Participants `[REQUIRED]`

- **Trigger Event**: `<API call, schedule, Kafka topic, or threshold breach>`
- **Participants / Swimlanes**: `<Actors, workers, stores>`
- **Diagram Reference**: `[<workflow-diagram.md>](<workflow-diagram.md>)` (`DIAG-...`)

## 2. Step-by-Step Execution & State Transitions `[REQUIRED]`

| Step | Actor / Component | Input / Precondition | Action & Side Effect | Next State / Output | Failure / Compensation |
|---|---|---|---|---|---|
| `1` | `<Actor/Service>` | `<State>` | `<Action>` | `<Output / Topic / State>` | `<Retry / DLQ / Rollback>` |

## 3. Asynchronous Semantics, Timeouts & Idempotency `[CONDITIONAL: Required for async, streaming, or batch workflows]`

- **Delivery Guarantee**: `<At-least-once + idempotent key>`
- **Backoff / Retry Budget**: `<Bounded retries + DLQ>`
- **Iteration / Time Bounds**: `<Hard loop/timeout limits>`
