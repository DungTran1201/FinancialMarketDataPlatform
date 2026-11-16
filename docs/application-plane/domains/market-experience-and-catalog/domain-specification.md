---
doc_id: APP-DOM-MKT-SPEC-001
title: "Domain Specification: Market Experience & Data Catalog"
doc_type: specification
plane: application-plane
scope_level: domain
domain: market-experience-and-catalog
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
    - "src/serving/api/modules/analytics/presentation/router.py"
    - "src/serving/api/modules/catalog/presentation/router.py"
related_docs:
  - APP-DOM-MKT-001
  - CAP-APP-MKT-DOC-001
  - CAP-APP-CAT-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Defined query/catalog domain scope, cross-plane read delegation, and AS-IS mock/fallback behaviors."
---

# Domain Specification: Market Experience & Data Catalog

## 1. Domain Responsibilities (`AS-IS`)

1. **Market & Historical Serving (`CAP-APP-MKT-001`)**: Exposes quotes, orderbook depth, 24h snapshots (with hot Redis -> OLAP fallback), bounded kline/trade queries, backfill job triggering, VWAP/volatility/correlation quant summaries, and anomaly evaluation, paired with `#/market-analytics` (`MarketAnalyticsModule.ts`).
2. **Catalog & Governance (`CAP-APP-CAT-001`)**: Manages monitored trading instruments, multi-tier staleness checks, manual Silver/DQ lakehouse execution, and lineage/watermark/Gold exploration via `#/data-management` (`DataManagementModule.ts`).

## 2. Known `AS-IS` Functional Fallbacks & Defects

- `GET /market/orderbook/{symbol}` returns static hardcoded bids/asks when missing from Redis while claiming `meta.source="redis_hot_cache"`.
- `POST /historical/backfill-jobs` hardcodes `"transport_mode": "MOCKED_SIMULATED_EXCHANGE_REST"` and executes synchronously inline before returning `202`.
- `GET /analytics/statistics/{symbol}` ignores `window` inside ClickHouse computation while echoing caller input.
- `GET /historical/klines/{symbol}` and `POST /market/ingest` fail with HTTP `500` on invalid ISO timestamp strings because `datetime.fromisoformat` lacks `try/except ValueError`.
- Zero endpoints enforce RBAC `Depends` checks (`SEC-AUDIT-003`).
