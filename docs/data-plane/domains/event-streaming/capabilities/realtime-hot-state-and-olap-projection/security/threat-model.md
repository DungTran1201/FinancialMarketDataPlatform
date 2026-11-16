---
doc_id: CAP-DP-STR2-TM-001
title: "Threat Model: Hot Cache, OLAP Sink & Anomaly Detector"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/streaming/consumers/hot_redis.py"
    - "src/streaming/consumers/anomaly_detector.py"
    - "src/serving/api/modules/analytics/presentation/router.py"
related_docs:
  - CAP-DP-STR2-SEC-001
  - DIAG-DP-STR2-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Analyzed cache eviction spoofing, unauthenticated cache eviction/anomaly triggers, and Redis Lua data overwrite bug."
---

# Threat Model: Hot Cache, OLAP Sink & Anomaly Detector

Derived threat diagram: [threat-model-diagram.md](threat-model-diagram.md) (`DIAG-DP-STR2-TM-001`).

## 1. Assets, Entry Points & Trust Boundaries `[REQUIRED]`

- **Assets**: Hot quotes/orderbooks, OHLCV rollups, statistical anomaly queue, Redis/ClickHouse credentials.
- **Entry Points & Trust Boundaries**: HTTP API callers (`POST /market/evict/{symbol}`, `POST /analytics/anomalies/evaluate`) and streaming consumers (`market.raw.*`, `market.anomalies.v1`).

## 2. Threat Scenarios, Mitigations & Residual Risks `[REQUIRED]`

| Threat ID | Scenario & Surface | Severity | Mitigations & Gaps | Residual Risk |
|---|---|---|---|---|
| `THR-STR2-001` | Unauthenticated HTTP caller invokes `POST /api/v1/market/evict/{symbol}` forcing repeated OLAP fallbacks or `POST /analytics/anomalies/evaluate` injecting synthetic alerts. | `CRITICAL` | **GAP (`SEC-AUDIT-003`)**: Zero JWT/RBAC enforcement on either endpoint. | `CRITICAL` (`BLOCKED`) |
| `THR-STR2-002` | Out-of-order replay overwrites newer market price with stale quotes. | `HIGH` | `HotStateProjector` monotonic check & `REDIS_MONOTONIC_UPSERT_LUA`. (**Bug**: price-less `ORDER_BOOK` writes `last_price="0"` to Lua at `hot_redis.py:193-198`.) | `MEDIUM` (until Lua price bug fixed) |
