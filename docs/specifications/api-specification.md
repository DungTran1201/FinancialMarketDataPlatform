# API Specification

## 1. Overview & Conventions

The Backend Application Plane exposes a versioned REST and WebSocket API implemented in **FastAPI**. All client applications (web dashboards, CLI clients, external integrations) interact exclusively through this API layer; direct client connections to Kafka, Redis, ClickHouse, PostgreSQL, or MinIO are strictly prohibited.

### Base URL & Versioning
- **REST Base Path**: `/api/v1`
- **WebSocket Base Path**: `/ws/v1`
- **Content-Type**: `application/json; charset=utf-8`
- **Timestamps**: ISO-8601 UTC (`YYYY-MM-DDTHH:mm:ss.sssZ`)
- **Monetary Values**: String-encoded exact decimals (`"89420.50000000"`) to preserve precision across JavaScript/JSON clients.

---

## 2. Cross-Cutting API Policies

### 2.1. Authentication & Authorization
- **User Authentication**: Bearer JWT (`Authorization: Bearer <access_token>`) issued via `POST /api/v1/auth/token`, verified via `POST /api/v1/auth/verify`, revoked via `POST /api/v1/auth/revoke` (`PBKDF2-HMAC-SHA256`, `210,000` iterations, `HS256` JWT). Note: `/api/v1/users` is not implemented.
- **Service / Programmatic Access**: Scoped API Keys managed via `POST /api/v1/auth/api-keys` (SHA-256 digest persisted).
- **Role-Based Access Control (RBAC)** *(Design Matrix — Runtime Enforcement Partial)*:
  - `viewer`: Read-only access to Market, Historical, and Analytics endpoints.
  - `analyst`: `viewer` permissions + permission to trigger on-demand Agent analysis runs and read Agent reports.
  - `operator`: `analyst` permissions + permission to manage monitored symbols and trigger historical backfill jobs.
  - `admin`: Full platform configuration, security domain inspection, and API-key administration.
  - **Runtime Disclosure (`PROP-APP-004`)**: While `/api/v1/auth/*` and `ControlledToolGateway` enforce tokens/roles, non-IAM domain routers do not yet attach FastAPI route-level JWT/RBAC `Depends(...)` guards (`runtime_rbac_enforced: false`).

### 2.2. Pagination, Filtering, and Query Guardrails
- **Cursor / Time-Range Pagination**: Historical time-series endpoints enforce `BoundedTimeRange` limits (`start_time`, `end_time`, `limit` max `1,000` klines / `500` trades).
- **Unbounded Query Rejection**: Any historical or analytical request lacking time bounds or exceeding the maximum window span (`90d` max analytics lookback) is rejected with `HTTP 422 Unprocessable Entity`.
- **Rate Limiting (`SlidingWindowRateLimiter` in `src/serving/api/main.py`)**: Enforced across 4 path buckets:
  - `/api/v1/auth*`: `10 requests / minute`
  - `/api/v1/agents/runs*`: `5 requests / minute`
  - `/api/v1/analytics*`: `30 requests / minute`
  - Default across all other endpoints (Market, Historical, Catalog, Observability, Data Platform, Microservices): `120 requests / minute`

### 2.3. Standard Envelope & Error Format (RFC 7807 Problem Details Compatible)

#### Successful Response Envelope
```json
{
  "data": { ... },
  "meta": {
    "request_id": "req_01JCF8Q92Z7P3M8N",
    "source": "redis_hot_cache",
    "as_of": "2026-11-12T02:58:00.123Z",
    "is_stale": false
  }
}
```

#### Error Response Envelope
```json
{
  "error": {
    "code": "QUERY_RANGE_EXCEEDED",
    "message": "Requested interval '1m' range exceeds maximum synchronous limit of 1000 data points.",
    "details": {
      "max_limit": 1000,
      "requested_window_minutes": 4320
    },
    "request_id": "req_01JCF8Q92Z7P3M8N",
    "timestamp": "2026-11-12T02:58:01.000Z"
  }
}
```

---

## 3. Domain Endpoint Catalog

### 3.1. Market Domain (Hot Data Path — Backed by Redis with ClickHouse Fallback)

| ID & Status | Method | Path | Description | Auth Role Target | Timeout | Target Source |
|---|---|---|---|---|---|---|
| `API-001` (`IMPLEMENTED`) | `GET` | `/api/v1/market/prices/{symbol}` | Get latest price and staleness metadata for a symbol (`?provider=binance`). | `viewer`+ | `1.5s` | Redis (`Fallback: ClickHouse`) |
| `API-031` (`IMPLEMENTED`) | `GET` | `/api/v1/market/prices` | Batch fetch latest prices for multiple symbols (`?symbols=BTCUSDT,ETHUSDT`). | `viewer`+ | `2.0s` | Redis Pipeline |
| `API-002` (`IMPLEMENTED`) | `GET` | `/api/v1/market/snapshots/{symbol}` | Get unified real-time market snapshot (24h ticker + best bid/ask + spread). | `viewer`+ | `2.0s` | Redis Hash/JSON |
| `API-032` (`IMPLEMENTED`) | `GET` | `/api/v1/market/orderbook/{symbol}` | Get latest top-N order book depth (`?depth=20`). | `viewer`+ | `1.5s` | Redis |
| `API-033` (`IMPLEMENTED`) | `POST` | `/api/v1/market/ingest` | Ingest a canonical market payload directly into the hot path pipeline. | `operator`+ | `2.0s` | `MarketIngestion` |
| `API-034` (`IMPLEMENTED`) | `POST` | `/api/v1/market/evict/{symbol}` | Evict hot cache entry for resilience/fallback verification. | `operator`+ | `1.5s` | Redis Adapter |
| `API-003` (`PLANNED`) | `WS` | `/ws/v1/market/stream` | `PLANNED` multiplexed WebSocket stream subscribing to live market updates. *(Not yet wired in FastAPI; see `/ws/v1/observability/stream` for active WS.)* | `viewer`+ | Persistent | Redis Pub/Sub (`PLANNED`) |

### 3.2. Historical Data Domain (Analytics Path — Backed by ClickHouse)

| ID & Status | Method | Path | Description | Auth Role Target | Timeout | Target Source |
|---|---|---|---|---|---|---|
| `API-004` (`IMPLEMENTED`) | `GET` | `/api/v1/historical/klines/{symbol}` | Query historical OHLCV candles (`?interval=1m&start_time=...&end_time=...&limit=500`). | `viewer`+ | `5.0s` | ClickHouse |
| `API-005` (`IMPLEMENTED`) | `GET` | `/api/v1/historical/trades/{symbol}` | Query historical executed trades (`?start_time=...&end_time=...&limit=500`). | `viewer`+ | `5.0s` | ClickHouse |
| `API-006` (`IMPLEMENTED`) | `POST` | `/api/v1/historical/backfill-jobs` | Submit an asynchronous historical backfill task (`202 Accepted` in v0.1). | `operator`+ | `3.0s` | Watermark Store / In-memory Job Store (PG Target) |
| `API-035` (`IMPLEMENTED`) | `GET` | `/api/v1/historical/backfill-jobs/{job_id}` | Poll status and watermark progress of a backfill job. | `operator`+ | `2.0s` | Watermark / Job Store |

### 3.3. Analytics Domain (Backed by ClickHouse & Quant Adapters)

| ID & Status | Method | Path | Description | Auth Role Target | Timeout | Target Source |
|---|---|---|---|---|---|---|
| `API-007` (`IMPLEMENTED`) | `GET` | `/api/v1/analytics/statistics/{symbol}` | Get rolling volatility, VWAP, return distribution, and volume profile (`?window=24h`). | `viewer`+ | `5.0s` | ClickHouse MV + Cache |
| `API-036` (`IMPLEMENTED`) | `GET` | `/api/v1/analytics/correlations` | Compute pairwise return correlation matrix (`?symbols=BTCUSDT,ETHUSDT&interval=1h&lookback_days=30`). | `viewer`+ | `8.0s` | ClickHouse / Quant Engine |
| `API-037` (`IMPLEMENTED`) | `GET` | `/api/v1/analytics/anomalies` | List detected market and data-quality anomalies. | `viewer`+ | `3.0s` | Anomaly Detector Store |
| `API-038` (`IMPLEMENTED`) | `POST` | `/api/v1/analytics/anomalies/evaluate` | Evaluate a market series for statistical return/volatility anomalies. | `analyst`+ | `3.0s` | `StatisticalAnomalyDetector` |
| *(`PLANNED`)* | `POST/GET` | `/api/v1/analytics/jobs*` | `PLANNED` asynchronous heavy correlation/analytics job queue (not yet mounted in `main.py`). | `analyst`+ | `3.0s` | PostgreSQL + Worker (`PLANNED`) |

### 3.4. Agent Intelligence & Reporting Domain

| ID & Status | Method | Path | Description | Auth Role Target | Timeout | Execution Pattern |
|---|---|---|---|---|---|---|
| `API-008` (`IMPLEMENTED`) | `POST` | `/api/v1/agents/runs` | Trigger a LangGraph 5-node investigation (`202 Accepted`). | `analyst`+ | `3.0s` | In-Process Async / Queue Target |
| `API-009` (`IMPLEMENTED`) | `GET` | `/api/v1/agents/runs/{run_id}` | Get workflow status, executed tool trail, token usage, and structured report. | `analyst`+ | `2.0s` | Run Store (PG Target) |
| `API-043` (`IMPLEMENTED`) | `GET` | `/api/v1/agents/runs/{run_id}/events` | Server-Sent Events (SSE) stream emitting step transitions and tool progress. | `analyst`+ | Stream | SSE |
| `API-044` (`IMPLEMENTED`) | `GET` | `/api/v1/reports` | List historical structured intelligence reports. | `viewer`+ | `3.0s` | Report Store |
| `API-045` (`IMPLEMENTED`) | `GET` | `/api/v1/reports/{run_id}` | Get detailed evidence-backed intelligence report by `run_id`. | `viewer`+ | `2.0s` | Report Store |

### 3.5. Platform Management, Data Catalog, IAM & Health Domain

| ID & Status | Method | Path | Description | Auth Role Target | Timeout | Target Source |
|---|---|---|---|---|---|---|
| `API-039` (`IMPLEMENTED`) | `GET` | `/api/v1/catalog/instruments` | List configured trading instruments and active stream subscriptions. | `viewer`+ | `2.0s` | Catalog Store |
| `API-040` (`IMPLEMENTED`) | `PUT` | `/api/v1/catalog/instruments/{symbol}` | Enable/disable ingestion streams for a trading instrument. | `operator`+ | `3.0s` | Catalog Store |
| `API-041` (`IMPLEMENTED`) | `GET` | `/api/v1/catalog/freshness` | Get end-to-end data freshness and consumer lag status per dataset and symbol. | `viewer`+ | `2.0s` | Redis + ClickHouse |
| `API-042` (`IMPLEMENTED`) | `POST` | `/api/v1/catalog/lakehouse/pipeline` | Execute catalog-triggered Lakehouse medallion batch pass. | `operator`+ | `5.0s` | Lakehouse Engines |
| `API-025` (`IMPLEMENTED`) | `GET` | `/api/v1/platform/config` | Retrieve active non-secret platform runtime configuration. | `viewer`+ | `1.5s` | `PlatformConfig` |
| `API-026` (`IMPLEMENTED`) | `POST` | `/api/v1/auth/token` | Issue `HS256` JWT access token (`PBKDF2-HMAC-SHA256` verification). | Public | `1.5s` | IAM Service |
| `API-027` (`IMPLEMENTED`) | `POST` | `/api/v1/auth/verify` | Verify JWT token signature, expiry, and IP-HMAC binding. | Authenticated | `1.5s` | IAM Service |
| `API-028` (`IMPLEMENTED`) | `POST` | `/api/v1/auth/revoke` | Revoke JWT token via SHA-256 revocation set. | Authenticated | `1.5s` | IAM Revocation Store |
| `API-029` (`IMPLEMENTED`) | `POST` | `/api/v1/auth/api-keys` | Issue scoped `X-API-Key` credentials (SHA-256 digest stored). | `admin` | `2.0s` | IAM Store |
| `API-030` (`IMPLEMENTED`) | `GET` | `/api/v1/auth/domains` | Return HTTPS domain & AES-256-GCM masked internal binding topology. | `admin` | `1.5s` | IAM / Security Config |
| `API-010` (`IMPLEMENTED`) | `GET` | `/api/v1/health/live` | Liveness probe (FastAPI event loop responsiveness). | Public | `1.0s` | In-Process |
| `API-023` (`IMPLEMENTED`) | `GET` | `/api/v1/health/ready` | Readiness probe (dependency state reporting). | Public | `2.0s` | Dependency Checks |
| `API-024` (`IMPLEMENTED`) | `GET` | `/metrics` | Root Prometheus OpenMetrics scrape endpoint (`10` `fmdp_*` metrics). | Public | `1.5s` | `DataObservabilityMetricsCollector` |

### 3.6. Real-Time Observatory, Data Platform v0.1 & Microservices (`FEAT-001` & `ADR-007`)

| ID & Status | Method | Path | Description | Auth Target | Timeout | Target Source |
|---|---|---|---|---|---|---|
| `API-017` (`IMPLEMENTED`) | `GET` | `/api/v1/observability/overview` | Non-mutating KPI summary, freshness & cached TCP infrastructure probe. | Public/Viewer | `2.0s` | `PipelineTraceRegistry` + TCP Prober |
| `API-018` (`IMPLEMENTED`) | `GET` | `/api/v1/observability/topology` | Parallel-branch DAG nodes & edges. | Public/Viewer | `2.0s` | `PlatformRuntimeContainer` |
| `API-019` (`IMPLEMENTED`) | `GET` | `/api/v1/observability/kafka` | Kafka Cluster, Broker status, partitions, CG lag & DLQ. | Public/Viewer | `1.5s` | `PartitionedEventStreamingBroker` |
| `API-020` (`IMPLEMENTED`) | `GET` | `/api/v1/observability/storage` | `.local_lakehouse` Bronze/Silver/Gold Parquet & Iceberg v2 manifests + ClickHouse/Redis stats. | Public/Viewer | `2.5s` | Local FS + In-Memory Stores |
| `API-021` (`IMPLEMENTED`) | `GET` | `/api/v1/observability/latency` | Parallel branch stats (`avg/P50/P95/P99`), histogram & clickable buckets. | Public/Viewer | `2.0s` | `PipelineTraceRegistry` |
| `API-022` (`IMPLEMENTED`) | `GET` | `/api/v1/observability/traces` | Filterable event trace list. | Public/Viewer | `1.5s` | `PipelineTraceRegistry` |
| `API-051` (`IMPLEMENTED`) | `GET` | `/api/v1/observability/traces/{event_id}` | 10-timestamp per-event trace waterfall detail. | Public/Viewer | `1.5s` | `PipelineTraceRegistry` |
| `API-052` (`IMPLEMENTED`) | `GET` | `/api/v1/observability/candles` | Real OHLCV bars & `Decimal` timeframe rollups (`1m/5m/15m/1h/4h/1d`). | Public/Viewer | `2.0s` | `ClickHouseBatchSink` |
| `API-055` (`IMPLEMENTED`) | `GET` | `/api/v1/observability/stream` | Server-Sent Events (SSE) live push of snapshots & heartbeats. | Public/Viewer | Stream | `PipelineTraceRegistry` |
| `API-056` (`IMPLEMENTED`) | `WS` | `/ws/v1/observability/stream` | Bidirectional WebSocket live telemetry feed. | Public/Viewer | Stream | `PipelineTraceRegistry` |
| `API-053` (`IMPLEMENTED`) | `POST` | `/api/v1/observability/live/probe` | Explicit live TCP probe & optional real `api.binance.com` HTTPS kline pull (`LIVE` mode). | `operator` | `4.0s` | External Network |
| `API-054` (`IMPLEMENTED`) | `POST` | `/api/v1/observability/demo/emit` | Explicit `DEMO` simulation (`emit_batch`, `inject_dlq`, `flush_lakehouse`, `run_full_pipeline`). | `operator` | `5.0s` | `PlatformRuntimeContainer` |
| `API-011` (`IMPLEMENTED`) | `POST` | `/api/v1/data-platform/v01/run` | Execute 12-stage Data Platform v0.1 pipeline end-to-end. | `operator` | `10.0s` | `DataPlatformV01Pipeline` |
| `API-046` (`IMPLEMENTED`) | `GET` | `/api/v1/data-platform/v01/status` | Query current Data Platform v0.1 pipeline status. | `viewer` | `2.0s` | `DataPlatformV01Pipeline` |
| `API-012` (`IMPLEMENTED`) | `GET` | `/api/v1/data-platform/v01/gold/{mart_name}` | Query materialized Gold mart Parquet tables. | `viewer` | `3.0s` | `GoldLayerMartEngine` |
| `API-013` (`IMPLEMENTED`) | `POST` | `/api/v1/data-platform/v01/compaction` | Trigger Stage 9 Silver Parquet compaction + Iceberg v2 snapshot. | `operator` | `10.0s` | `SilverLakehouseMergeEngine` |
| `API-014` (`IMPLEMENTED`) | `GET` | `/api/v1/data-platform/v01/lineage` | Return Stage 12 dataset ownership & directed lineage graph. | `viewer` | `2.0s` | `DataLineageGovernanceRegistry` |
| `API-047` (`IMPLEMENTED`) | `GET` | `/api/v1/data-platform/v01/watermarks` | List persisted ingestion watermarks from SQLite/PG store. | `viewer` | `2.0s` | `IngestionWatermarkStore` |
| `API-048` (`IMPLEMENTED`) | `GET` | `/api/v1/data-platform/v01/metrics` | Export Data Platform v0.1 OpenMetrics `/metrics` exposition. | Public | `1.5s` | `DataObservabilityMetricsCollector` |
| `API-016` (`IMPLEMENTED`) | `GET` | `/api/v1/data-platform/v01/telemetry` | Structured JSON data-flow telemetry across Stages 1..12. | Public | `2.0s` | `DataPlatformV01Pipeline` |
| `API-015` (`IMPLEMENTED`) | `GET` | `/api/v1/microservices/topology` | Return 8-service topology manifest & AES-256-GCM masked internal bindings. | Public | `1.5s` | `MicroserviceRegistry` |
| `API-049` (`IMPLEMENTED`) | `GET` | `/api/v1/microservices/health` | Aggregate health probes across all 8 registered domain microservices. | Public | `2.0s` | `MicroserviceRegistry` |
| `API-050` (`IMPLEMENTED`) | `POST` | `/api/v1/microservices/dispatch/{service_id}` | Dispatch internal request via `IN_PROCESS_ASGI` or `REMOTE_HTTP_CONTAINER` mode. | `operator` | `5.0s` | `MicroserviceRegistry` |


