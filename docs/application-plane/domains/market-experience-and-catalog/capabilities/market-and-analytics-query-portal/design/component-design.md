---
doc_id: CAP-APP-MKT-COMP-001
title: "Component & Screen Design: Market, Historical, Analytics & MarketAnalyticsModule"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-MKT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: system-architect
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
  - CAP-APP-MKT-REQ-001
  - APP-ARCH-COMPAT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Detailed Market/Historical/Analytics FastAPI components and MarketAnalyticsModule UI defects."
---

# Component & Screen Design: Market, Historical, Analytics & MarketAnalyticsModule

## 1. Backend Presentation Modules (`src/serving/api/modules/`)

- **`market/presentation/router.py`**: Mounts `/prices/{symbol}`, `/prices`, `/snapshots/{symbol}`, `/orderbook/{symbol}`, `/ingest`, `/evict/{symbol}`. Uses `latest_price_handler` + `hot_redis_projector` -> `clickhouse_sink` fallback.
- **`historical/presentation/router.py`**: Mounts `/klines/{symbol}`, `/trades/{symbol}`, `/backfill-jobs`, `/backfill-jobs/{job_id}`. Validates windows via `BoundedTimeRange`.
- **`analytics/presentation/router.py`**: Computes `get_market_statistics_summary`, pairwise Pearson correlations via `compute_deterministic_pearson_correlation`, and Z-score anomalies via `runtime.anomaly_detector`.

## 2. Frontend Screen Specification: `#/market-analytics` (`MarketAnalyticsModule.ts`)

- **Panels Rendered**: Symbol selector & interval switcher (`1m`..`1d`), `CandlestickChart.ts`, L2 Orderbook bids/asks view, Quantitative KPIs (VWAP, Realized Volatility, Volume, Trade Count), Pairwise Correlation Heatmap, and Anomaly Evaluator/Table.
- **UI States & Verified Defects**:
  - Zero-value masking (`COMPAT-008`): UI expressions `|| 0.45`, `|| 0.012`, `|| 1440` replace valid `0` metrics with arbitrary constants.
  - Event listener leak (`COMPAT-008`): Re-rendering candlesticks attaches additional `window.addEventListener('resize', ...)` handlers without teardown cleanup.
  - Consumes `/api/v1/observability/candles` (dual float + string OHLCV) for charting rather than `/api/v1/historical/klines/{symbol}` strings.
