---
doc_id: CAP-APP-MKT-NFR-001
title: "Non-Functional Requirements: Market & Analytics Query Portal"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-MKT-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/historical/presentation/router.py"
    - "src/serving/api/modules/market/presentation/router.py"
related_docs:
  - CAP-APP-MKT-REQ-001
  - APP-OPS-SLO-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented read-path determinism, query pagination bounds, and unestablished throughput SLOs."
---

# Non-Functional Requirements: Market & Analytics Query Portal

## 1. Bounded Execution & Precision Constraints (`AS-IS`)

- **Pagination Bounds**: `/historical/klines` and `/trades` enforce `1 <= limit <= 1000`; `/orderbook` constrains `5 <= depth <= 20`.
- **Precision Integrity**: Restores string-encoded Decimal semantics across quotes, OHLCV bars, and VWAP outputs.
- **Blocking Request Anti-Pattern (`GAP`)**: `POST /market/ingest` and `POST /historical/backfill-jobs` execute storage writes synchronously before returning `202 Accepted`.

## 2. Target Latency & Concurrency Targets (`OPEN`)

- Exact p95 read/analytics latency targets and concurrent query limits remain **`OPEN`** pending benchmark profiling (`APP-OPS-SLO-001`).
