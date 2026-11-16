---
doc_id: DIAG-APP-MKT-STATE-001
title: "State Machine Diagram: Backfill Job Execution States (AS-IS vs Target)"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-MKT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: business-analyst
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/market-experience-and-catalog/capabilities/market-and-analytics-query-portal/use-cases/uc-mkt-002-query-klines-trades-and-backfill.md"
related_docs:
  - CAP-APP-MKT-UC-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Rendered synchronous AS-IS backfill job transition alongside target async queue states."
---

# State Machine Diagram: Backfill Job Execution States (`AS-IS` vs Target)

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-MKT-STATE-001` |
| **Title & Purpose** | Backfill Job Lifecycle (`AS-IS` Synchronous `202` vs `TARGET` Queued Worker) |
| **Owner Role & Scope** | `fullstack-engineer / CAP-APP-MKT-001` |
| **Authoritative Source** | [uc-mkt-002-query-klines-trades-and-backfill.md](../use-cases/uc-mkt-002-query-klines-trades-and-backfill.md) (`CAP-APP-MKT-UC-002`) |
| **Notation** | `Mermaid stateDiagram-v2` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
stateDiagram-v2
    [*] --> AcceptedInline : "POST /historical/backfill-jobs"
    AcceptedInline --> COMPLETED : "AS-IS inline fetch + Kafka/Redis/CH/Bronze write finishes before HTTP 202 return"
    AcceptedInline --> FailedException : "Uncaught REST or fromisoformat error -> HTTP 500"
    COMPLETED --> [*]
    FailedException --> [*]
```

## 3. Legend

- **`AS-IS` Shortcut**: HTTP `202` returns directly with `"status": "COMPLETED"` in `runtime.backfill_jobs`; asynchronous `QUEUED -> RUNNING -> COMPLETED` worker transitions are `NOT_IMPLEMENTED`.
