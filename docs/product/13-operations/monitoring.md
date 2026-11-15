# Monitoring, Metrics & Alerting Specification — Real-Time Data Flow Observatory

| Document Metadata | Value |
|---|---|
| **Document ID** | `OPS-MON-001` |
| **Title** | `Real-Time Data Platform Observatory, Telemetry APIs & AS-IS Gap Specification` |
| **Version** | `1.0.0` |
| **Status** | `DRAFT` (`[PROPOSED — NOT APPROVED]`) |
| **Authoring Role** | `architecture-modeler` |
| **Review Role** | `security-reviewer` |
| **Created Date** | `2026-11-15` |
| **Updated Date** | `2026-11-15` |
| **Work Item Reference** | `work-items/FEAT-001-realtime-monitoring-and-data-flow-dashboard/` |
| **Canonical Model Reference** | `models/deployment/deployment.yaml` |
| **Source References** | `src/shared/observability/tracing.py`, `src/shared/observability/metrics.py`, `src/serving/infrastructure/runtime.py`, `src/serving/api/gateway/observability.py` |

---

## 1. Purpose `[MANDATORY]`

Defines Prometheus OpenMetrics histograms, unified `EventLifecycleTrace` correlation rules, parallel-branch End-to-End (E2E) serving latency calculation, Observatory REST/SSE/WebSocket telemetry contracts, and honest `AS-IS` vs `UNAVAILABLE` runtime disclosures for `FEAT-001`.

---

## 2. Scope & Boundaries `[MANDATORY]`

Applies to `/api/v1/observability/*`, `/ws/v1/observability/stream`, `/metrics`, and `PlatformRuntimeContainer` tracing telemetry. Demo UI routes (`/ui/*`) are decommissioned.

---

## 3. Metrics & SLI/SLO Baseline Catalog `[MANDATORY]`

| Metric Name | Type | Labels | Alert Threshold |
|---|---|---|---|
| `fmdp_ingested_events_total` | `Counter` | `provider`, `symbol`, `event_type` | Rate drop `== 0` for `> 5m` |
| `fmdp_dlq_events_total` | `Counter` | `provider`, `error_code` | Increment rate `> 5/min` |
| `fmdp_consumer_lag_records` | `Gauge` | `consumer_group`, `topic` | `> 1000` uncommitted records |
| `fmdp_hot_out_of_order_dropped_total` | `Counter` | `provider` | Spike `> 50/min` |
| `fmdp_dq_validation_runs_total` | `Counter` | `dataset`, `status` | `status="FAILED"` `>= 1` |
| `fmdp_gold_mart_rows_total` | `Gauge` | `mart_name` | `== 0` after Bronze flush |
| `fmdp_stage_processing_duration_ms` | `Histogram` | `stage`, `mode` | Stage P95 `> 250ms` |
| `fmdp_end_to_end_latency_ms` | `Histogram` | `path`, `mode` | Critical E2E P95 `> 500ms` |
| `fmdp_stage_events_total` | `Counter` | `stage`, `status`, `mode` | `status="FAILED"` `> 1%` |
| `fmdp_serving_requests_total` | `Counter` | `endpoint`, `status` | `status="5xx"` `> 0` |

### 3.1 Parallel-Branch Latency Formula (Non-Summation Rule)

Because Kafka consumers (`cg.hot.redis.v1`, `cg.analytics.clickhouse.v1`, `cg.lakehouse.bronze.v1`) process events **in parallel**, the Observatory never sums all sink durations sequentially:

- `serial_spine_ms = ingestion + kafka_publish + kafka_consume`
- `hot_branch_ms = redis_hot_write`
- `olap_branch_ms = clickhouse_olap_write`
- `lakehouse_branch_ms = bronze_archive + silver_merge + dq_gate + gold_mart`
- `end_to_end_serving_ms = serial_spine_ms + max(active parallel branches) + serving_ready`

### 3.2 AS-IS Runtime Capabilities vs Unavailable Components

| Component | AS-IS Runtime Reality | Honest UI Classification |
|---|---|---|
| API & UI Server | FastAPI + Uvicorn in-process Modular Monolith | `ACTIVE` / `IN_PROCESS` |
| Kafka Broker 1 | In-process 6-partition `PartitionedEventStreamingBroker` + optional `:9092` TCP probe | `IN_PROCESS_ACTIVE` or `LIVE_CONTAINER` |
| Kafka Brokers 2 & 3 | Not deployed in single-node KRaft `docker-compose.yml` (`KAFKA_NODE_ID=1`) | `UNAVAILABLE` |
| Redis & ClickHouse | In-memory stores (`HotStateProjector`, `ClickHouseBatchSink`) + `:6379`/`:8123` TCP probe | `IN_PROCESS` or `LIVE_CONTAINER` / `UNAVAILABLE` |
| Lakehouse (Bronze/Silver/Gold) | Real ZSTD Parquet files & Apache Iceberg v2 manifests under `.local_lakehouse/` | `ACTIVE` (disk-backed) |
| External Binance Feed | Explicit `POST /api/v1/observability/live/probe` with `fetch_binance=true` vs Demo button | `LIVE` vs `DEMO` / `UNAVAILABLE` |

---

## 4. Assumptions `[MANDATORY]`

- **ASSUMP-01**: High-cardinality trace identifiers (`event_id`, `correlation_id`) are retained strictly in the bounded in-memory `PipelineTraceRegistry` (`maxlen=2000`) and excluded from Prometheus metric labels (`DATA-RULE-010`). `[ASSUMPTION — REQUIRES VALIDATION]`

---

## 5. Open Questions `[MANDATORY]`

- **OQ-01**: Production distributed tracing across separate container processes will require OpenTelemetry OTLP context propagation once multi-process deployment profiles are enabled. `[OPEN QUESTION]`

---

## 6. Dependencies `[MANDATORY]`

- **Upstream Dependencies**: `models/deployment/deployment.yaml`, `models/api/api.yaml`, `models/ux/ux.yaml`, `.agents/rules/data-platform-observability.md`.
- **Downstream Consumers**: Operators inspecting SCR-003 (`/data-flow` in `frontend/` SPA), `/api/v1/observability/*`, and Prometheus `/metrics`.

---

## 7. Bidirectional Traceability `[MANDATORY]`

| Upstream Artifact ID | Current Artifact ID | Downstream Artifact ID | Verification Reference |
|---|---|---|---|
| `FR-04`, `NFR-001` | `OPS-MON-001` | `API-017`..`API-022`, `SCR-001` | `TC-015` (`tests/integration/test_realtime_observability_dashboard.py`) |

---

## 8. Approval & Baseline Sign-Off `[CONDITIONAL]`

| Reviewer Role | Reviewer Name / Agent | Review Decision | Date | Evidence / Notes |
|---|---|---|---|---|
| `security-reviewer` | `security-reviewer` | `[PROPOSED — NOT APPROVED]` | `2026-11-15` | Verified strict `/ui/*` CSP isolation and zero high-cardinality Prometheus labels. |

