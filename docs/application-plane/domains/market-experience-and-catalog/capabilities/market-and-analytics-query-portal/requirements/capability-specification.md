---
doc_id: CAP-APP-MKT-REQ-001
title: "Capability Specification: Market & Analytics Query Portal"
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
    - "src/serving/api/modules/analytics/presentation/router.py"
    - "frontend/src/modules/market-analytics/MarketAnalyticsModule.ts"
related_docs:
  - CAP-APP-MKT-DOC-001
  - CAP-APP-MKT-RULE-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Authored atomic FRs and observed AS-IS gaps for Market, Historical, Analytics & MarketAnalyticsModule UI."
---

# Capability Specification: Market & Analytics Query Portal

## 1. Capability Scope & `AS-IS` Reality

Serves low-latency hot quotes, orderbook depth, 24h market summaries, historical OHLCV klines/trades, on-demand backfill jobs, quant metrics (VWAP, realized volatility, Pearson correlation, Z-score anomalies), and the `#/market-analytics` UI screen.

## 2. Functional Requirements

| Req ID | Requirement Statement | `AS-IS` Evidence | Target / Gap |
|---|---|---|---|
| `FR-MKT-001` | System MUST serve latest price & 24h snapshot from hot state, falling back cleanly to OLAP on cache miss and reporting actual data source in `meta.source`. | `market/router.py:24-111` | `GET /orderbook/{symbol}` returns static hardcoded bids/asks when missing while still reporting `meta.source="redis_hot_cache"`. |
| `FR-MKT-002` | System MUST validate bounded historical time ranges (`max_window_days <= 365`, `limit <= 1000`) and return Decimal-serialized klines and trades. | `historical/router.py:28-107` | Invalid `start_time`/`end_time` ISO syntax triggers unguarded `500` instead of `422`; `get_historical_trades` reads private `_trades_table`. |
| `FR-MKT-003` | System MUST allow operators to trigger backfill jobs (`POST /historical/backfill-jobs`), raw ingest (`POST /market/ingest`), and hot eviction (`POST /market/evict/{symbol}`). | `historical/router.py:109-163`, `market/router.py:134-188` | Synchronous execution inside `202`; hardcoded `MOCKED_SIMULATED_EXCHANGE_REST` tag; zero RBAC enforcement. |
| `FR-MKT-004` | System MUST compute VWAP, realized volatility, pairwise Pearson correlation matrices, and Z-score anomaly evaluations deterministically. | `analytics/router.py:26-126` | `get_symbol_statistics` echoes caller `window` while querying unwindowed stats. |
| `FR-MKT-005` | `#/market-analytics` UI MUST render interactive candlestick chart, L2 depth, statistics cards, correlation matrix, and anomaly table without masking zero values. | `MarketAnalyticsModule.ts` | Uses `|| 0.45` / `|| 0.012` / `|| 1440` fallbacks masking genuine `0` metrics and leaks duplicate `window.resize` listeners (`COMPAT-008`). |
