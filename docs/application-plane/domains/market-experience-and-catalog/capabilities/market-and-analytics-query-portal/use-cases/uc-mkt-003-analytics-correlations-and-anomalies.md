---
doc_id: CAP-APP-MKT-UC-003
title: "Use Case UC-MKT-003: Compute Statistics, Correlations & Anomaly Evaluation"
doc_type: specification
plane: application-plane
scope_level: use-case
domain: market-experience-and-catalog
capability_id: CAP-APP-MKT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/analytics/presentation/router.py"
    - "frontend/src/modules/market-analytics/MarketAnalyticsModule.ts"
related_docs:
  - CAP-APP-MKT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented analytics statistics, Pearson correlation matrix, anomaly reads, and inline series evaluation."
---

# Use Case UC-MKT-003: Compute Statistics, Correlations & Anomaly Evaluation

## 1. Main Analytics Flows

1. **Quantitative Statistics (`GET /analytics/statistics/{symbol}`)**: Queries `runtime.get_market_statistics_summary(provider, symbol, window)` -> returns `vwap`, `realized_volatility`, `total_base_volume`, `total_quote_volume`, `trade_count` (`404 ERR_ANALYTICS_NOT_FOUND` on miss; *Note*: ClickHouse helper ignores `window` internally).
2. **Correlation Matrix (`GET /analytics/correlations?symbols=...`)**: Extracts close price arrays per symbol from `clickhouse_sink` and runs `compute_deterministic_pearson_correlation`.
3. **List & Evaluate Anomalies (`GET /analytics/anomalies`, `POST /analytics/anomalies/evaluate`)**: Reads `runtime.detected_anomalies` or submits custom `values: float[]` through `anomaly_detector.evaluate_series`; if triggered, appends to memory list and publishes to `market.anomalies.v1`. *(Note: `POST` mutates anomaly queue without auth `AS-IS`.)*

## 2. Exception Flows & Security Note

- **`404 ERR_ANALYTICS_NOT_FOUND`**: Returned when ClickHouse OLAP holds zero closed bars or trades for the target symbol.
- **Unauthenticated Mutation**: `POST /analytics/anomalies/evaluate` appends anomalies to runtime state and Kafka without RBAC checks (`SEC-AUDIT-003`).
