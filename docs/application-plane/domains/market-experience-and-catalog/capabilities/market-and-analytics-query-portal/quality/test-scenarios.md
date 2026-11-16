---
doc_id: CAP-APP-MKT-TS-001
title: "Test Scenarios: Market & Analytics Query Portal"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-MKT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: qa-lead
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/integration/test_three_planes_framework.py"
    - "tests/contract/test_contracts_and_guardrails.py"
related_docs:
  - CAP-APP-MKT-DOC-001
  - CAP-APP-MKT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Documented backend ASGI tests and missing MarketAnalyticsModule frontend UI verification."
---

# Test Scenarios: Market & Analytics Query Portal

## 1. Covered Backend Scenarios (`AS-IS`)

- **`TS-MKT-001`**: Ingest raw trade/kline -> query `/market/prices/{symbol}` from hot Redis -> `POST /market/evict/{symbol}` -> confirm fallback read returns `clickhouse_fallback`.
- **`TS-MKT-002`**: Query `/historical/klines/{symbol}` within valid window (`200`) and exceeding `max_window_days` (`422 ERR_INVALID_TIME_RANGE`); execute `POST /historical/backfill-jobs` and poll `GET`.
- **`TS-MKT-003`**: Query `/analytics/statistics/{symbol}`, `/correlations`, and trigger anomaly evaluation (`POST /analytics/anomalies/evaluate`).

## 2. Verification Gaps

- No test covers invalid `start_time` HTTP `500` handling, non-hardcoded `/orderbook` misses, or `#/market-analytics` zero-masking UI regressions (`node` absent in workspace).
