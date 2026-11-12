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
- **User Authentication**: Bearer JWT (`Authorization: Bearer <access_token>`) issued via `/api/v1/auth/token`.
- **Service / Programmatic Access**: Scoped API Keys via `X-API-Key` header hashed and validated against PostgreSQL/Redis cache.
- **Role-Based Access Control (RBAC)**:
  - `viewer`: Read-only access to Market, Historical, and Analytics endpoints.
  - `analyst`: `viewer` permissions + permission to trigger on-demand Agent analysis runs and read Agent reports.
  - `operator`: `analyst` permissions + permission to manage monitored symbols and trigger historical backfill jobs.
  - `admin`: Full platform configuration, user management, and security audit access.

### 2.2. Pagination, Filtering, and Query Guardrails
- **Cursor / Time-Range Pagination**: Historical time-series endpoints require explicit `start_time` and `end_time` bounds, `limit` (default `100`, maximum `1000`), and optional `cursor`.
- **Unbounded Query Rejection**: Any historical or analytical request lacking time bounds or exceeding the maximum window span per interval (e.g., max 7 days for `1m` candles in a single synchronous call, or max 5,000 trade ticks) is rejected with `HTTP 422 Unprocessable Entity`.
- **Rate Limiting**: Enforced via Redis sliding-window counters per user/API key:
  - Market & Historical Read Endpoints: `120 requests / minute`
  - Heavy Analytical Endpoints: `30 requests / minute`
  - Agent On-Demand Trigger Endpoints: `5 requests / minute`

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

| Method | Path | Description | Auth Role | Timeout | Target Source |
|---|---|---|---|---|---|
| `GET` | `/api/v1/market/prices/{symbol}` | Get latest price and staleness metadata for a symbol (`?provider=binance`). | `viewer`+ | `1.5s` | Redis (`Fallback: ClickHouse`) |
| `GET` | `/api/v1/market/prices` | Batch fetch latest prices for multiple symbols (`?symbols=BTCUSDT,ETHUSDT`). | `viewer`+ | `2.0s` | Redis Pipeline |
| `GET` | `/api/v1/market/snapshots/{symbol}` | Get unified real-time market snapshot (24h ticker + best bid/ask + top-5 order book + latest 1m candle). | `viewer`+ | `2.0s` | Redis Hash/JSON |
| `GET` | `/api/v1/market/orderbook/{symbol}` | Get latest top-N order book depth (`?depth=20`). | `viewer`+ | `1.5s` | Redis |
| `WS` | `/ws/v1/market/stream` | Multiplexed WebSocket stream subscribing to live ticker/kline/trade updates pushed from Redis Pub/Sub / Kafka fanout. | `viewer`+ | Persistent | Redis Pub/Sub |

### 3.2. Historical Data Domain (Analytics Path — Backed by ClickHouse)

| Method | Path | Description | Auth Role | Timeout | Target Source |
|---|---|---|---|---|---|
| `GET` | `/api/v1/historical/klines/{symbol}` | Query historical OHLCV candles (`?interval=1m&start_time=...&end_time=...&limit=500`). | `viewer`+ | `5.0s` | ClickHouse |
| `GET` | `/api/v1/historical/trades/{symbol}` | Query historical executed trades (`?start_time=...&end_time=...&limit=500&cursor=...`). | `viewer`+ | `5.0s` | ClickHouse |
| `POST` | `/api/v1/historical/backfill-jobs` | Submit an asynchronous historical backfill task (`Idempotency-Key` required). | `operator`+ | `3.0s` | PostgreSQL + Airflow Trigger |
| `GET` | `/api/v1/historical/backfill-jobs/{job_id}` | Poll status and watermark progress of a backfill job. | `operator`+ | `2.0s` | PostgreSQL |

### 3.3. Analytics Domain (Backed by ClickHouse & Materialized Views)

| Method | Path | Description | Auth Role | Timeout | Target Source |
|---|---|---|---|---|---|
| `GET` | `/api/v1/analytics/statistics/{symbol}` | Get rolling volatility, VWAP, return distribution, and volume profile (`?window=24h`). | `viewer`+ | `5.0s` | ClickHouse MV + Redis Cache (TTL 15s) |
| `GET` | `/api/v1/analytics/correlations` | Compute pairwise return correlation matrix across requested symbols (`?symbols=BTCUSDT,ETHUSDT,SOLUSDT&interval=1h&lookback_days=30`). | `viewer`+ | `8.0s` | ClickHouse |
| `GET` | `/api/v1/analytics/anomalies` | List detected market and data-quality anomalies (`?symbol=BTCUSDT&severity=HIGH`). | `viewer`+ | `3.0s` | ClickHouse / PostgreSQL |
| `POST` | `/api/v1/analytics/jobs` | Enqueue an asynchronous heavy analytical computation job when lookback window exceeds synchronous limits. | `analyst`+ | `3.0s` | PostgreSQL + Worker |
| `GET` | `/api/v1/analytics/jobs/{job_id}` | Retrieve status and result payload of an asynchronous analytical job. | `analyst`+ | `2.0s` | PostgreSQL |

### 3.4. Agent Intelligence Domain (Asynchronous Execution — Backed by Agent Service & PostgreSQL)

| Method | Path | Description | Auth Role | Timeout | Execution Pattern |
|---|---|---|---|---|---|
| `POST` | `/api/v1/agents/runs` | Trigger an asynchronous LangGraph investigation or market analysis workflow (`Idempotency-Key` header supported). Returns `202 Accepted` with `run_id`. | `analyst`+ | `3.0s` | Async Enqueue |
| `GET` | `/api/v1/agents/runs/{run_id}` | Get current workflow status, executed tool trail, token usage, and structured report (when `COMPLETED`). | `analyst`+ | `2.0s` | PostgreSQL Read |
| `GET` | `/api/v1/agents/runs/{run_id}/events` | Server-Sent Events (SSE) stream emitting real-time step transitions and tool execution progress for an active run. | `analyst`+ | Stream | SSE (PostgreSQL / Redis Pub/Sub) |
| `GET` | `/api/v1/agents/reports` | List historical structured intelligence reports with provenance filters (`?symbol=BTCUSDT&trigger_mode=EVENT_TRIGGERED`). | `viewer`+ | `3.0s` | PostgreSQL |

### 3.5. Platform Management & Data Catalog Domain (Backed by PostgreSQL)

| Method | Path | Description | Auth Role | Timeout | Target Source |
|---|---|---|---|---|---|
| `GET` | `/api/v1/catalog/instruments` | List configured trading instruments and active stream subscriptions. | `viewer`+ | `2.0s` | PostgreSQL (Cached 60s) |
| `PUT` | `/api/v1/catalog/instruments/{symbol}` | Enable/disable ingestion streams for a trading instrument. | `operator`+ | `3.0s` | PostgreSQL |
| `GET` | `/api/v1/catalog/freshness` | Get end-to-end data freshness and consumer lag status per dataset and symbol. | `viewer`+ | `2.0s` | Redis + ClickHouse |
| `GET` | `/api/v1/health/live` | Liveness probe (verifies FastAPI event loop responsiveness). | Public | `1.0s` | In-Process |
| `GET` | `/api/v1/health/ready` | Readiness probe (verifies connectivity to PostgreSQL, ClickHouse, Redis, and Kafka). | Public | `2.0s` | Dependency Checks |

