---
doc_id: DP-OPS-OBS-001
title: "Data Plane SLIs, SLO Status & Prometheus Cardinality Rules"
doc_type: specification
plane: data-plane
scope_level: plane
status: DRAFT
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
    - "deploy/observability/prometheus/alerts.yml"
    - "src/shared/config/settings.py"
related_docs:
  - DP-ARCH-OBS-001
  - OVR-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Recorded concrete implemented SLIs/thresholds vs OPEN unapproved SLO targets."
---

# Data Plane SLIs, SLO Status & Prometheus Cardinality Rules

## 1. Service Level Indicators & Alert Thresholds

| SLI | PromQL / Computation Source (`AS-IS`) | Alert / Configured Threshold | SLO Target Status |
|---|---|---|---|
| **DLQ Event Rate** | `increase(fmdp_dlq_events_total[5m])` | `> 10` for `1m` (`alerts.yml:11`) | Threshold defined in `alerts.yml`; overall SLA `%` `OPEN` |
| **Consumer Record Lag** | `fmdp_consumer_lag_records` | `> 5000` for `2m` (`alerts.yml:19`) | Threshold defined in `alerts.yml`; overall SLA `OPEN` |
| **Hot Cache Staleness** | `now_utc - latest_ingested_at` vs `market_staleness_threshold_ms` | `15000 ms` (`settings.py:21`) | Freshness threshold configured; production SLO `%` `OPEN` |
| **E2E Stage Latency (`t0`–`t9`)** | `fmdp_end_to_end_latency_ms` & `PipelineTraceRegistry` | Query filter default `slow_threshold_ms=25.0` (`observability.py:96`) | Percentile SLO (`p95`/`p99`) `OPEN` (must not invent targets) |

## 2. Bounded Label Cardinality Rule

Metrics MUST NEVER attach unbounded per-event labels (`event_id`, `trade_id`, `request_id`, raw IPs). Enforced in `test_realtime_observability_dashboard.py:183-189`.
