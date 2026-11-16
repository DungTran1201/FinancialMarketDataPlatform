---
doc_id: CAP-DP-STR2-SPEC-001
title: "Capability Specification: Realtime Hot State, OLAP Projection & Anomaly Detection"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/streaming/consumers/hot_redis.py"
    - "src/streaming/consumers/analytics_ch.py"
    - "src/streaming/consumers/anomaly_detector.py"
related_docs:
  - CAP-DP-STR-002-ROOT
  - CAP-DP-STR2-RULE-001
requirement_ids:
  - FR-STR2-001
  - FR-STR2-002
  - FR-STR2-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Specified HotStateProjector, ClickHouseBatchSink, and StatisticalAnomalyDetector behavior vs simulation gaps."
---

# Capability Specification: Realtime Hot State, OLAP Projection & Anomaly Detection

## 1. Capability Scope & `AS-IS` Reality `[REQUIRED]`

Maintains serving-ready hot state (`latest price`, `24h snapshot`, `top-20 orderbook`), deduplicated OLAP tables & timeframe rollups (`1m` -> `5m`/`15m`/`1h`/`4h`/`1d`), and statistical z-score anomaly alerts (`market.anomalies.v1`). **Current Reality**: Executed 100% in memory via Python dicts (`HotStateProjector`, `ClickHouseBatchSink`, `StatisticalAnomalyDetector`).

## 2. Functional Requirements `[REQUIRED]`

| Req ID | Requirement Statement | `AS-IS` Code Evidence | Known Gap / Defect |
|---|---|---|---|
| `FR-STR2-001` | `HotStateProjector` MUST reject out-of-order stale events (`incoming_ts < current_ts`) while updating `_price_store`, `_snapshot_store`, and `_orderbook_store`. | `hot_redis.py:124-187` (Python dicts + Lua script `for i = 3, #ARGV, 2`) | Live Redis client unused (`_redis_client=None`); `_sync_record_to_live_redis` skips snapshot/orderbook keys and writes `last_price="0"` on price-less orderbooks. |
| `FR-STR2-002` | `ClickHouseBatchSink` MUST deduplicate ingested trades/klines/tickers via `ReplacingMergeTree` semantics, support bucketed OHLCV rollups (`query_klines`), and compute VWAP & aggregate statistics. | `analytics_ch.py:123-383` (in-memory dicts) | `_clickhouse_client` unused; `flush_interval_ms` timer unimplemented; `get_storage_snapshot()` checks `_table` instead of `event_type` (`0` pending rows); JSON persistence omits trades/tickers. |
| `FR-STR2-003` | `StatisticalAnomalyDetector` MUST compute Bessel sample z-score on `len(values) >= 5`, emit `EventEnvelopeV1(ANOMALY)` when `abs(z_score) >= threshold`, and suppress duplicates within `900s` cooldown. | `anomaly_detector.py:47-115` | Cooldown stored in-memory dict (not Redis); no live worker consumes `market.anomalies.v1`. |
