# 11 — Reliability and Observability Architecture

## 1. Reliability Engineering & Failure Isolation

The platform is engineered so that **single-component failures degrade gracefully rather than causing cascading system outages**.

### 1.1. Failure Modes, Blast Radius, and Automated Recovery

| Component Failure | Blast Radius | Immediate System Behavior | Automated Recovery / Operator Runbook |
|---|---|---|---|
| **Binance WebSocket Drop** | Affected collector stream only | Hot cache serves last price; after `15s` sets `meta.is_stale = true`. | `collector-ws` reconnects with exponential backoff + jitter ($1\text{s} \rightarrow 30\text{s}$) and records a gap window in `ingestion_watermarks` for `collector-rest` backfill. |
| **Redis Container Crash / Eviction** | Hot cache latency only | `MarketQueryService` catches `RedisError` / miss and transparently queries ClickHouse via a rate-limited circuit breaker (`meta.source = "clickhouse_fallback"`). | When Redis recovers, `consumer-hot-redis` immediately repopulates hot state from live Kafka events within seconds. |
| **ClickHouse Temporary Outage / Restart** | Historical & Analytics APIs (`HTTP 503`); Hot Price API unaffected | `backend-api` serves `/api/v1/market/prices` and `/snapshots` from Redis; `consumer-analytics-ch` pauses offset commits and retains messages safely in Kafka (`168h` / `7 days` raw retention; `720h` / `30 days` anomalies/DLQ). | Once ClickHouse is healthy, `consumer-analytics-ch` drains the Kafka backlog in micro-batches without data loss. |
| **MinIO / Lakehouse (`Spark/Airflow PLANNED`) Outage** | Batch Lakehouse updates paused | Real-time ingestion, Redis hot serving, ClickHouse real-time analytics, and Agent tools continue at **100% normal operation**. | `consumer-lakehouse-bronze` resumes flushing from last committed Kafka offset; scheduled batch jobs (`PLANNED`) re-run idempotently. |
| **External LLM Provider Outage / Rate Limit** | Agent narrative synthesis only | Data Plane and Market/Historical/Analytics APIs are **100% unaffected**. `agent-worker` trips circuit breaker and emits a deterministic quantitative fallback summary (`DEGRADED_DETERMINISTIC_ONLY`). | Circuit breaker probes LLM recovery after cooldown (`60s`). |

---

## 2. Observability Pillars: Metrics, Logs, Traces, and Alerts

### 2.1. Structured Logging Standard
All Python services (`collector-*`, `consumer-*`, `backend-api`, `agent-worker`) emit structured JSON logs to `stdout` with mandatory correlation fields:
```json
{
  "timestamp": "2026-11-12T02:58:00.123Z",
  "level": "INFO",
  "service": "backend-api",
  "environment": "local",
  "request_id": "req_01JCF8Q92Z7P3M8N",
  "run_id": null,
  "module": "market.application.queries",
  "event": "market_price_read",
  "symbol": "BTCUSDT",
  "source": "redis_hot_cache",
  "latency_ms": 3.42
}
```
- **Secret Redaction**: Logging processors automatically mask fields matching `password`, `secret`, `token`, `api_key`, and `authorization`.

### 2.2. Implemented Prometheus Metrics Catalog (`src/shared/observability/metrics.py`)

Exposed via `/metrics` on `backend-api:8000` (`API-016`) and `/api/v1/data-platform/v01/metrics` on `svc-data-plane-v01:8007` (`DataObservabilityMetricsCollector`):

| Metric Name (`IMPLEMENTED`) | Type | Labels / Key Attributes | Purpose |
|---|---|---|---|
| `fmdp_ingested_events_total` | Counter | `provider`, `symbol`, `event_type` | Tracks validated raw market events ingested per stream. |
| `fmdp_dlq_events_total` | Counter | `provider`, `event_type`, `reason` | Tracks schema/normalization errors routed to `market.dlq.v1`. |
| `fmdp_consumer_lag_records` | Gauge | `consumer_group`, `topic`, `partition` | Measures unconsumed message backlog per consumer group. |
| `fmdp_hot_out_of_order_dropped_total` | Counter | `provider`, `symbol` | Tracks stale out-of-order updates dropped by monotonic guard (`BR-003`). |
| `fmdp_dq_validation_runs_total` | Counter | `dataset`, `status` | Tracks passing vs blocking runs of `DataQualityGateEngine`. |
| `fmdp_gold_mart_rows_total` | Gauge | `mart_name` | Tracks materialized record count across Gold analytical marts. |
| `fmdp_serving_requests_total` | Counter | `service`, `endpoint`, `status` | Tracks API/microservice request volume and response outcomes. |
| `fmdp_stage_events_total` | Counter | `stage`, `status` | Tracks processed event counts per 12-stage Data Platform v0.1 step. |
| `fmdp_stage_processing_duration_ms` | Histogram/Summary | `stage` | Measures execution latency across each pipeline stage. |
| `fmdp_end_to_end_latency_ms` | Histogram/Summary | `pipeline` | Measures end-to-end ingestion-to-serving latency in milliseconds. |

**Target / Conceptual Metrics (`PLANNED` — Not Yet Exported by Runtime)**:
- `collector_ws_reconnects_total`, `market_redis_fallback_total`, `clickhouse_batch_insert_duration_ms`, `http_request_duration_seconds`, `agent_workflow_duration_seconds`, `agent_tool_invocations_total`, `agent_llm_tokens_total`.

---

## 3. Alerting Thresholds (`deploy/observability/prometheus/alerts.yml`)

| Alert Name & Status | Condition (PromQL) | Severity | Operational Action |
|---|---|---|---|
| **`FMDPDeadLetterQueueSpike`** (`IMPLEMENTED`) | `increase(fmdp_dlq_events_total[5m]) > 10` for `1m` | `warning` (`PLANE-A`) | Inspect `market.dlq.v1` payload envelope for upstream Binance schema changes or malformed payloads. |
| **`FMDPConsumerLagHigh`** (`IMPLEMENTED`) | `fmdp_consumer_lag_records > 5000` for `2m` | `critical` (`PLANE-A`) | Inspect sink write latency (ClickHouse/Redis/Lakehouse) and scale consumer group workers up to partition count (`6`). |
| **`MarketDataStaleHigh`** (`PLANNED`) | Concept: source event age `> 30s` for `1m` | `CRITICAL` | Verify `collector-ws` health and exchange status; trigger REST gap-fill. |
| **`RedisFallbackActive`** (`PLANNED`) | Concept: sustained ClickHouse fallback rate `> 0` for `1m` | `HIGH` | Check Redis container health and `volatile-lru` eviction stats. |
| **`APILatencyP99Breach`** (`PLANNED`) | Concept: P99 HTTP latency `> 500ms` over `5m` | `WARNING` | Identify slow route and inspect ClickHouse `system.query_log`. |
| **`AgentTokenBudgetExceeded`** (`PLANNED`) | Concept: 24h LLM token quota exceeded | `WARNING` | Circuit breaker pauses non-critical event-triggered LLM runs. |

