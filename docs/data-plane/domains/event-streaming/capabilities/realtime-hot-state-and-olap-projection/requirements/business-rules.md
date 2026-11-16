---
doc_id: CAP-DP-STR2-RULE-001
title: "Business Rules: Monotonic Hot Cache, ReplacingMergeTree & Z-Score Cooldown"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: business-analyst
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
  - CAP-DP-STR2-SPEC-001
requirement_ids:
  - RULE-STR2-001
  - RULE-STR2-002
  - RULE-STR2-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented exact monotonic Lua condition, ClickHouse deduplication version columns, and Bessel z-score formula."
---

# Business Rules: Monotonic Hot Cache, ReplacingMergeTree & Z-Score Cooldown

## 1. Domain Rules `[REQUIRED]`

| Rule ID | Condition / Formula | Context | Consequence | Related FR |
|---|---|---|---|---|
| `RULE-STR2-001` | Upsert allowed iff missing `exchange_event_time_ms` OR `incoming_ts >= current_ts` (`hot_redis.py:24,127-130`). | Hot quote/orderbook updates | Stale event dropped and `dropped_out_of_order_count` + Prometheus `fmdp_hot_out_of_order_dropped_total` incremented. | `FR-STR2-001` |
| `RULE-STR2-002` | ClickHouse sink deduplicates trades by `(provider, symbol, trade_id)` keeping newest `ingested_at`, and klines by `(provider, symbol, interval, open_time)` keeping newest `exchange_event_time`. | `analytics_ch.py:152-200` | Preserves idempotency on replay; older timestamps skipped cleanly. | `FR-STR2-002` |
| `RULE-STR2-003` | Given `values[:-1]` (`N >= 4`), `variance = sum((x-mean)^2) / max(1, len-1)`, `std_dev = sqrt(variance) > 1e-12`, `z_score = (latest - mean) / std_dev`. Emit `CRITICAL` if `abs(z) >= 3.5` else `HIGH` when `abs(z) >= 2.5`, guarded by `900s` cooldown key `agent:cooldown:{provider}:{symbol}:{detector}`. | `anomaly_detector.py:44-114` | Cooldown suppresses duplicate alert emission and increments `suppressed_alerts_count`. | `FR-STR2-003` |

## 2. OHLCV Rollup Precision Rule

Multi-timeframe candle rollups (`query_klines`) aggregate `open = first.open`, `high = max(highs)`, `low = min(lows)`, `close = last.close`, `volume = sum(volumes)` using fixed-point `Decimal` (`analytics_ch.py:240-284`).
