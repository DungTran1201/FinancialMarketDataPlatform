---
doc_id: CAP-APP-CAT-NFR-001
title: "Non-Functional Requirements: Instrument & Data Catalog"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-CAT-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/catalog/presentation/router.py"
    - "deploy/postgres/init/01_schema.sql"
related_docs:
  - CAP-APP-CAT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Recorded catalog durability gap and open latency/persistence targets."
---

# Non-Functional Requirements: Instrument & Data Catalog

## 1. Durability & Consistency Reality (`AS-IS`)

- **Durability Gap**: Instrument updates made via `PUT /api/v1/catalog/instruments/{symbol}` vanish on container restart until Postgres `monitored_instruments` is wired (`OPEN-CAT-001`).
- **Key Normalization**: Router keys `runtime.monitored_instruments[sym]` by uppercase `symbol` only, whereas Postgres `monitored_instruments` enforces `UNIQUE(provider, symbol)` — storing multi-provider pairs under one symbol would collide in memory `AS-IS`.

## 2. Target Latency & Availability SLOs (`OPEN`)

- Exact freshness poll latency and metadata cache TTL policies remain **`OPEN`**.
