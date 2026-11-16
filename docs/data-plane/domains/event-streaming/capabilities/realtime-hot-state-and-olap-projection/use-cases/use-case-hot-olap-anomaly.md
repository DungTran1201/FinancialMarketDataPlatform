---
doc_id: CAP-DP-STR2-UC-001
title: "Use Case: Project Monotonic Hot State, Flush OLAP Micro-Batches & Detect Anomalies"
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
  - UC-STR2-001
  - AC-STR2-001
  - AC-STR2-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented hot state monotonic guard, OLAP deduplication, and anomaly suppression flows."
---

# Use Case: `UC-STR2-001` — Project Monotonic Hot State, Flush OLAP Micro-Batches & Detect Anomalies

## 1. Identification & Traceability `[REQUIRED]`

- **Use Case ID**: `UC-STR2-001`
- **Primary Actor**: Consumer pipeline (`DataPlatformV01Pipeline` or HTTP `/analytics/anomalies/evaluate`)
- **Parent Requirements**: `FR-STR2-001`..`003` (`RULE-STR2-001`..`003`)

## 2. Trigger, Preconditions & Postconditions `[REQUIRED]`

- **Trigger**: Consumers receive `EventEnvelopeV1` records or anomaly evaluator receives numeric series (`len >= 5`).
- **Preconditions**: Broker has published records or HTTP caller provides >=5 sample floats.
- **Success Postconditions**: Latest hot state updated iff monotonic; OLAP dicts deduplicated by natural/version key; anomaly envelope emitted iff `|z| >= 2.5` and cooldown expired.
- **Failure Postconditions**: Stale timestamps dropped silently (metric incremented); cooldown suppression skips alert emit.

## 3. Main Success, Alternative & Exception Flows `[REQUIRED]`

1. `HotStateProjector.project_event(ev)` validates `incoming_ts >= current_ts` (`RULE-STR2-001`) and updates `_price_store`/`_snapshot_store`/`_orderbook_store`.
2. `ClickHouseBatchSink.ingest_event(ev)` + `flush()` deduplicates into `_trades_table`/`_klines_table`/`_tickers_table` (`RULE-STR2-002`).
3. `StatisticalAnomalyDetector.evaluate_series()` evaluates Bessel z-score (`RULE-STR2-003`) and publishes `EventEnvelopeV1(ANOMALY)` on threshold breach.

| Branch ID | Condition | System Behavior | Outcome |
|---|---|---|---|
| `ALT-1` | Out-of-order older price event | Skips update, increments `dropped_out_of_order_count` & Prometheus counter. | Hot state preserved monotonic |
| `EXC-1` | Second anomaly within `900s` | `expires_at > now_ts` -> increments `suppressed_alerts_count`, returns `(None, None)`. | Cooldown enforced |

- **Acceptance Criteria (`AC-STR2-001`, `AC-STR2-002`)**: Stale event drops verified (`test_gap_recovery_and_dlq.py`); `ReplacingMergeTree` dedup & 15m cooldown verified (`test_three_planes_framework.py`).
