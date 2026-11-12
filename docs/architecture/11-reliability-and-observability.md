# 11 — Reliability and Observability Architecture

## 1. Reliability Engineering & Failure Isolation

The platform is engineered so that **single-component failures degrade gracefully rather than causing cascading system outages**.

### 1.1. Failure Modes, Blast Radius, and Automated Recovery

| Component Failure | Blast Radius | Immediate System Behavior | Automated Recovery / Operator Runbook |
|---|---|---|---|
| **Binance WebSocket Drop** | Affected collector stream only | Hot cache serves last price; after `15s` sets `meta.is_stale = true`. | `collector-ws` reconnects with exponential backoff + jitter ($1\text{s} \rightarrow 30\text{s}$) and records a gap window in `ingestion_watermarks` for `collector-rest` backfill. |
| **Redis Container Crash / Eviction** | Hot cache latency only | `MarketQueryService` catches `RedisError` / miss and transparently queries ClickHouse via a rate-limited circuit breaker (`meta.source = "clickhouse_fallback"`). | When Redis recovers, `consumer-hot-redis` immediately repopulates hot state from live Kafka events within seconds. |
| **ClickHouse Temporary Outage / Restart** | Historical & Analytics APIs (`HTTP 503`); Hot Price API unaffected | `backend-api` serves `/api/v1/market/prices` and `/snapshots` from Redis; `consumer-analytics-ch` pauses offset commits and retains messages safely in Kafka (72h retention). | Once ClickHouse is healthy, `consumer-analytics-ch` drains the Kafka backlog in micro-batches without data loss. |
| **MinIO / Spark / Airflow Outage** | Batch Lakehouse updates paused | Real-time ingestion, Redis hot serving, ClickHouse real-time analytics, and Agent tools continue at **100% normal operation**. | `consumer-lakehouse-bronze` resumes flushing from last committed Kafka offset; Airflow re-runs failed DAG tasks idempotently. |
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

### 2.2. Prometheus Metrics Catalog (`/metrics`)

| Metric Name | Type | Labels | Purpose |
|---|---|---|---|
| `collector_events_ingested_total` | Counter | `provider`, `symbol`, `event_type` | Tracks raw ingestion throughput per symbol. |
| `collector_ws_reconnects_total` | Counter | `provider`, `stream` | Detects unstable external WebSocket connections. |
| `collector_validation_errors_total` | Counter | `provider`, `event_type`, `reason` | Tracks schema violations routed to `market.dlq.v1`. |
| `kafka_consumer_group_lag` | Gauge | `consumer_group`, `topic`, `partition` | Measures unconsumed message backlog per consumer group. |
| `market_hot_path_lag_ms` | Histogram | `provider`, `symbol` | End-to-end latency from `exchange_event_time` to Redis update. |
| `clickhouse_batch_insert_duration_ms` | Histogram | `table` | Tracks bulk insert performance and merge pressure in ClickHouse. |
| `http_request_duration_seconds` | Histogram | `method`, `route`, `status_code` | Tracks P50, P95, and P99 API latency per endpoint. |
| `market_redis_fallback_total` | Counter | `symbol`, `reason` | Tracks how often hot reads fall back to ClickHouse (`miss` vs `error`). |
| `agent_workflow_duration_seconds` | Histogram | `trigger_mode`, `status` | Measures end-to-end LangGraph execution duration. |
| `agent_tool_invocations_total` | Counter | `tool_name`, `status` | Tracks deterministic tool usage, timeouts, and errors. |
| `agent_llm_tokens_total` | Counter | `provider`, `model`, `token_type` | Monitors prompt and completion token consumption for cost governance. |

---

## 3. Alerting Thresholds (Grafana / Prometheus Alertmanager)

| Alert Name | Condition (PromQL Summary) | Severity | Automated / Operator Action |
|---|---|---|---|
| `MarketDataStaleHigh` | `(time() - market_latest_event_timestamp_seconds) > 30` for 1m | `CRITICAL` | Verify `collector-ws` health and Binance API status; trigger REST gap-fill. |
| `KafkaConsumerLagElevated` | `kafka_consumer_group_lag > 25000` for 3m | `WARNING` | Inspect ClickHouse insert latency or scale consumer group replicas. |
| `DeadLetterQueueGrowing` | `rate(collector_validation_errors_total[5m]) > 0` | `WARNING` | Inspect `market.dlq.v1` payload for upstream Binance schema changes. |
| `RedisFallbackActive` | `rate(market_redis_fallback_total{reason="error"}[1m]) > 0` | `HIGH` | Check Redis container health and memory eviction stats. |
| `APILatencyP99Breach` | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.5` | `WARNING` | Identify slow query route and inspect ClickHouse `system.query_log`. |
| `AgentTokenBudgetExceeded` | `increase(agent_llm_tokens_total[24h]) > 500000` | `WARNING` | Circuit breaker pauses non-critical event-triggered LLM runs. |

