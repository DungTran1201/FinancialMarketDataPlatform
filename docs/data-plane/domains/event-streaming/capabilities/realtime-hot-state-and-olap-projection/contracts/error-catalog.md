---
doc_id: CAP-DP-STR2-ERR-001
title: "Error Catalog: Hot State, OLAP Sink & Anomaly Detector"
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
  - CAP-DP-STR2-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Documented stale drop, empty series handling, and zero std_dev handling."
---

# Error Catalog: Hot State, OLAP Sink & Anomaly Detector

## 1. Error & Suppression Conditions `[REQUIRED]`

| Condition | Code Path | Behavior | Monitoring / Consumer Impact |
|---|---|---|---|
| **Out-of-Order Price Frame** | `hot_redis.py:127-130` | Drops event (`return False`), increments `dropped_out_of_order_count`. | Logged in Prometheus `fmdp_hot_out_of_order_dropped_total`. |
| **Insufficient Series / Flat Variance (`std_dev <= 1e-12`)** | `anomaly_detector.py:56-66` | Safely skips division by zero; returns `(None, None)`. | No anomaly alert emitted. |

## 2. Live Database Driver Note

Because `_redis_client` and `_clickhouse_client` are un-wired (`None`), connection-refused/retry exceptions are not yet exercised or handled.
