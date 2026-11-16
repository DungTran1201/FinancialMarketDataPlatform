---
doc_id: CAP-APP-MKT-ERR-001
title: "Error Catalog: Market, Historical & Quantitative Analytics"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-MKT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/market/presentation/router.py"
    - "src/serving/api/modules/historical/presentation/router.py"
    - "src/serving/api/modules/analytics/presentation/router.py"
related_docs:
  - APP-ERR-SHARED-001
  - CAP-APP-MKT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented HTTP error codes and unguarded ISO date ValueError defect."
---

# Error Catalog: Market, Historical & Quantitative Analytics

## 1. Domain Module Errors (`{ "detail": { "code", "message" } }`)

| HTTP | Error Code | Endpoint(s) | Trigger |
|---|---|---|---|
| `404` | `ERR_SYMBOL_NOT_FOUND` | `GET /market/prices/{symbol}` | Neither hot cache nor OLAP holds symbol |
| `404` | `ERR_SNAPSHOT_NOT_FOUND` | `GET /market/snapshots/{symbol}` | No snapshot in Redis or ClickHouse |
| `404` | `ERR_JOB_NOT_FOUND` | `GET /historical/backfill-jobs/{job_id}` | Job ID absent from `runtime.backfill_jobs` |
| `404` | `ERR_ANALYTICS_NOT_FOUND` | `GET /analytics/statistics/{symbol}` | Zero OHLCV bars/trades for symbol |
| `422` | `ERR_INVALID_TIME_RANGE` | `GET /historical/klines/{symbol}` | `BoundedTimeRange` violation (`start > end` or exceeds `max_window_days`) |

## 2. Unhandled Error Defect (`AS-IS`)

- Supplying malformed `start_time`/`end_time` to `GET /historical/klines/{symbol}` or `ingested_at` to `POST /market/ingest` calls `datetime.fromisoformat(...)` outside `try/except`, leaking HTTP `500`.
