---
doc_id: DP-ARCH-OBS-001
title: "Data Plane Observability, Tracing & Alerting Architecture"
doc_type: specification
plane: data-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/shared/observability/metrics.py"
    - "src/shared/observability/tracing.py"
    - "deploy/observability/prometheus/prometheus.yml"
    - "deploy/observability/prometheus/alerts.yml"
related_docs:
  - DP-ARCH-001
  - DP-OPS-OBS-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Cataloged DataObservabilityMetricsCollector metrics, t0-t9 parallel branch math, alerts.yml, and Grafana Compose mount gap."
---

# Data Plane Observability, Tracing & Alerting Architecture

## 1. 10-Timestamp Event Lifecycle (`PipelineTraceRegistry`, `tracing.py`)

Tracks every traced event across `CANONICAL_STAGES` (`t0`–`t9`) in a bounded in-memory `deque(maxlen=2000)` guarded by `threading.RLock`:

- **Serial Spine**: `t0` (`exchange_event_time`) -> `t1` (`ingested_at`) -> `t2` (`normalized_at`) -> `t3` (`kafka_produced_at`).
- **Parallel Fan-Out Branches**:
  - Hot Branch: `t3 -> t4` (`redis_projected_at`), end-to-end `(t9_or_t4 - t1)`.
  - OLAP Branch: `t3 -> t5` (`clickhouse_written_at`), end-to-end `(t9_or_t5 - t1)`.
  - Lakehouse Branch: `t3 -> t6` (`bronze_archived_at`) -> `t7` (`silver_merged_at`) -> `t8` (`gold_marts_updated_at`).
  - Serving Verification: `t9` (`serving_verified_at`).
- **Critical-Path Computation (`compute_parallel_branch_latencies`)**: Computes overall branch bottleneck `max(hot_branch, olap_branch)` rather than falsely summing parallel sink durations.

## 2. Prometheus Metrics (`DataObservabilityMetricsCollector`, `metrics.py`)

Exposes 10 isolated `CollectorRegistry` metrics via `GET /metrics` and `GET /api/v1/data-platform/v01/metrics` (**label cardinality rule**: never binds `event_id` or `trade_id`):

- Counters: `fmdp_ingested_events_total`, `fmdp_dlq_events_total`, `fmdp_hot_out_of_order_dropped_total`, `fmdp_dq_validation_runs_total`, `fmdp_gold_mart_rows_total`, `fmdp_stage_events_total`, `fmdp_serving_requests_total`.
- Gauges: `fmdp_consumer_lag_records`.
- Histograms: `fmdp_stage_processing_duration_ms`, `fmdp_end_to_end_latency_ms` (buckets `0.5`..`5000.0 ms`).

## 3. Scrape & Alert Rules (`deploy/observability/`)

- `prometheus.yml`: `scrape_interval: 15s`, `evaluation_interval: 15s`; targets `prometheus:9090`, `backend-api:8000/metrics`, `svc-data-plane-v01:8007/api/v1/data-platform/v01/metrics`.
- `alerts.yml` (`fmdp_data_platform_slis`):
  - `FMDPDeadLetterQueueSpike`: `increase(fmdp_dlq_events_total[5m]) > 10` for `1m` (`severity: warning`).
  - `FMDPConsumerLagHigh`: `fmdp_consumer_lag_records > 5000` for `2m` (`severity: critical`).
- **Configured vs. Wired Gap**: `deploy/observability/grafana/datasources/prometheus.yml` exists, but `docker-compose.yml:367-377` does NOT mount it into the `grafana` container, and zero JSON dashboard files exist.
