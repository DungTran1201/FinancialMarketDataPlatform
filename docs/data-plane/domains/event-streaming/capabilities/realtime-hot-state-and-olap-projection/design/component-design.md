---
doc_id: CAP-DP-STR2-COMP-001
title: "Component Design: HotStateProjector, ClickHouseBatchSink & AnomalyDetector"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: data-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/streaming/consumers/hot_redis.py"
    - "src/streaming/consumers/analytics_ch.py"
    - "src/streaming/consumers/anomaly_detector.py"
related_docs:
  - CAP-DP-STR2-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Documented internal projection stores, Lua args fix, rollup logic, and unused external client hooks."
---

# Component Design: HotStateProjector, ClickHouseBatchSink & AnomalyDetector

Derived DFD: [projection-dfd.md](projection-dfd.md) (`DIAG-DP-STR2-DFD-001`).

## 1. Component Decomposition `[REQUIRED]`

- `HotStateProjector` (`hot_redis.py:61-238`): Holds `_price_store`, `_snapshot_store`, `_orderbook_store` keyed by `market:v1:{kind}:{provider}:{symbol}`. Only calls `_sync_record_to_live_redis` on `price_key` when `_redis_client` is injected (`None` in runtime).
- `ClickHouseBatchSink` (`analytics_ch.py:43-383`): `MicroBatchBuffer` (`max_rows=5000`, `flush_interval_ms=1000` unscheduled) -> `flush()` merges rows into Python tables, serves `query_klines()` rollups and `compute_aggregated_statistics()`.
- `StatisticalAnomalyDetector` (`anomaly_detector.py:32-119`): Evaluates return z-score series with in-memory `_cooldown_registry`.

## 2. Verified Implementation Defects to Remediate Before Live Container Cutover `[REQUIRED]`

- `hot_redis.py:193-198` passes `"last_price", str(raw_price or "0")` to Redis Lua even on price-less `ORDER_BOOK` frames (unlike `_price_store` which skips `None`).
- `analytics_ch.py:306-308` inspects `r.get("_table")` while `ingest_event()` sets `"event_type"`, so pending buffer counts report `0`.
- All three worker `main()` entrypoints exit immediately (`hot_redis.py:241`, `analytics_ch.py:386`).
