---
doc_id: CAP-APP-MKT-RULE-001
title: "Business Rules: Market & Analytics Query Portal"
doc_type: specification
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
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/market/presentation/router.py"
    - "src/serving/api/modules/historical/presentation/router.py"
    - "src/shared/domain/primitives.py"
related_docs:
  - CAP-APP-MKT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented precision serialization, bounded time range, and staleness business rules."
---

# Business Rules: Market & Analytics Query Portal

## 1. Enforced Business Rules

| Rule ID | Business Rule | `AS-IS` Enforcement |
|---|---|---|
| `RULE-MKT-001` | Monetary prices, volumes, VWAP, and volatility values in module envelopes (`/market`, `/historical`, `/analytics`) MUST serialize as Decimal strings, not binary floats. | Enforced in `market/router.py`, `historical/router.py`, `analytics/router.py` (`str(...)`). Exception: `analytics.router.py` `z_score` & correlation floats; `/observability/candles` includes both floats & `*_str`. |
| `RULE-MKT-002` | Historical kline queries MUST constrain `(end_time - start_time)` via `BoundedTimeRange(max_span_seconds=max_window_days*86400)` with `limit <= 1000`. | Enforced via `BoundedTimeRange` -> HTTP `422 ERR_INVALID_TIME_RANGE`. |
| `RULE-MKT-003` | Quote `is_stale` evaluates against `PlatformConfig.market_staleness_threshold_ms` (`5000` ms default). | Enforced in `latest_price_handler`. |

## 2. Target Validation Improvements (`OPEN`)

- `RULE-MKT-004` (`OPEN`): Reject invalid ISO timestamps in `/historical/klines/{symbol}` and `/market/ingest` cleanly with HTTP `422` instead of HTTP `500`.
