# Platform API Contracts & Streaming Protocols

| Metadata | Value |
|---|---|
| **Document ID** | `DOC-CONTRACTS-API` |
| **Title** | Unified REST, WebSocket, SSE & Event Streaming Contracts |
| **Category** | Technical Specification |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-15` |
| **Authoring Role** | `api-architect` |

---

## 1. Edge API Gateway Endpoints (`svc-api-gateway` / Port 8000)

Authoritative specification: `models/api/api.yaml` and `docs/specifications/api-specification.md` (`55` implemented FastAPI routes + `1` `PLANNED` WebSocket route `API-003`). Note that non-IAM domain routers do not yet attach route-level JWT/RBAC `Depends(...)` guards (`runtime_rbac_enforced: false`, tracked under `PROP-APP-004`).

### 1.1. Core Market, Historical & Analytics Endpoints

| API ID | Method | Route | Description | Auth Target / Runtime | Owning Microservice Target |
|---|---|---|---|---|---|
| `API-010` | `GET` | `/api/v1/health/live` | FastAPI process liveness probe | Public | `svc-api-gateway:8000` |
| `API-023` | `GET` | `/api/v1/health/ready` | Platform dependency readiness probe | Public | `svc-api-gateway:8000` |
| `API-024` | `GET` | `/metrics` | Prometheus OpenMetrics telemetry endpoint (`10` `fmdp_*` metrics) | Public | `svc-api-gateway:8000` |
| `API-031` | `GET` | `/api/v1/market/prices` | Batch latest spot prices across requested symbols (`?symbols=...`) | `viewer`+ (`PROP-APP-004`) | `svc-market-hot:8001` |
| `API-001` | `GET` | `/api/v1/market/prices/{symbol}` | Latest price and staleness metadata with ClickHouse fallback | `viewer`+ (`PROP-APP-004`) | `svc-market-hot:8001` |
| `API-002` | `GET` | `/api/v1/market/snapshots/{symbol}` | Unified 24h market snapshot + best bid/ask | `viewer`+ (`PROP-APP-004`) | `svc-market-hot:8001` |
| `API-032` | `GET` | `/api/v1/market/orderbook/{symbol}` | Top-N level-2 order book depth (`?depth=20`) | `viewer`+ (`PROP-APP-004`) | `svc-market-hot:8001` |
| `API-004` | `GET` | `/api/v1/historical/klines/{symbol}` | Historical OHLCV candles with `BoundedTimeRange` limits | `viewer`+ (`PROP-APP-004`) | `svc-historical-backfill:8002` |
| `API-006` | `POST` | `/api/v1/historical/backfill-jobs` | Submit bounded historical backfill job | `operator`+ (`PROP-APP-004`) | `svc-historical-backfill:8002` |
| `API-007` | `GET` | `/api/v1/analytics/statistics/{symbol}` | Rolling volatility, VWAP, and return statistics | `viewer`+ (`PROP-APP-004`) | `svc-analytics-quant:8003` |
| `API-036` | `GET` | `/api/v1/analytics/correlations` | Cross-instrument Pearson correlation matrix | `viewer`+ (`PROP-APP-004`) | `svc-analytics-quant:8003` |

### 1.2. Observability, Data Plane & Topology Endpoints

| API ID | Method | Route | Description | Backing Microservice |
|---|---|---|---|---|
| `API-017` | `GET` | `/api/v1/observability/overview` | Live KPI summary, freshness & cached TCP infra probes | `backend-api:8000` |
| `API-018` | `GET` | `/api/v1/observability/topology` | Parallel-branch DAG nodes & edges | `backend-api:8000` |
| `API-055` | `GET` | `/api/v1/observability/stream` | Server-Sent Events (SSE) live push (`snapshot` / `heartbeat`) | `backend-api:8000` |
| `API-016` | `GET` | `/api/v1/data-platform/v01/telemetry` | Live Data Platform v0.1 pipeline flow telemetry | `svc-data-plane-v01:8007` |
| `API-015` | `GET` | `/api/v1/microservices/topology` | Runtime 8-service topology & `AS-IS` execution mode | `svc-api-gateway:8000` |

---

## 2. Real-Time Streaming Protocols

### 2.1. Live Observability WebSocket (`IMPLEMENTED` — `WS /ws/v1/observability/stream`) & Planned Market WS (`PLANNED` — `WS /ws/v1/market/stream`)
- **`IMPLEMENTED` (`API-056`)**: `WS /ws/v1/observability/stream` pushes live platform snapshots, event traces, and stage latencies directly to connected observability UIs.
- **`PLANNED` (`API-003`)**: `WS /ws/v1/market/stream` is the designed client market subscription channel (not yet mounted on the FastAPI app):
```json
{
  "action": "subscribe",
  "channels": ["trades:BTCUSDT", "orderbook:BTCUSDT", "ticker:BTCUSDT"]
}
```
Conceptual target market update broadcast envelope (`PLANNED` with `API-003`):
```json
{
  "channel": "trades:BTCUSDT",
  "timestamp": 1731638400000,
  "data": {
    "symbol": "BTCUSDT",
    "price": "92450.50",
    "quantity": "0.1540",
    "side": "buy",
    "trade_id": 84729103
  }
}
```

### 2.2. Server-Sent Events (SSE) Pipeline Stream (`GET /api/v1/observability/stream`)
Streams live event snapshots and heartbeats directly to the Frontend observatory (`API-055`):
```text
event: snapshot
data: {"mode": "SIMULATION", "events_processed": 124, "latency_ms": {...}}

event: heartbeat
data: {"timestamp": "2026-11-15T09:00:01.000Z"}
```

---

## 3. Kafka Event Envelope Specification (`models/data-platform/events.yaml`)

Every message published to Kafka follows the canonical `EventEnvelopeV1` contract (`src/shared/contracts/events/market_events.py`), ensuring deterministic idempotency via UUIDv5 and partition-level ordering (`provider:symbol` or `provider:symbol:interval`):

```json
{
  "schema_version": "1.0.0",
  "event_id": "b82fa76d-88b1-5f0e-a4b5-68051a37c024",
  "provider": "binance",
  "symbol": "BTCUSDT",
  "event_type": "kline",
  "exchange_event_time": "2026-11-15T09:00:00Z",
  "ingested_at": "2026-11-15T09:00:00.045000Z",
  "payload": {
    "interval": "1m",
    "open_time": "2026-11-15T08:59:00Z",
    "close_time": "2026-11-15T08:59:59.999000Z",
    "open_price": "92100.00000000",
    "high_price": "92550.00000000",
    "low_price": "92050.00000000",
    "close_price": "92450.50000000",
    "base_volume": "142.84500000",
    "quote_volume": "13205912.22500000",
    "trade_count": 3412,
    "taker_buy_base_volume": "78.10000000",
    "taker_buy_quote_volume": "7218500.00000000",
    "is_closed": true
  },
  "sequence_id": null
}
```

### 3.1. Dead Letter Queue Envelope (`market.dlq.v1`)

When payload validation or schema deserialization fails, the unparsed raw message is wrapped into `DeadLetterEnvelopeV1` (`src/shared/contracts/events/market_events.py`):
```json
{
  "dlq_id": "dlq-7c81a9f0-32b4-5d9e-bc41-89012a45d678",
  "source_provider": "binance",
  "source_stream": "market.raw.klines.v1",
  "error_type": "ValidationError",
  "error_message": "DECIMAL_PARSE_FAILURE: Invalid non-numeric price string",
  "raw_payload": "{\"e\":\"kline\",\"E\":1763197200000,\"s\":\"BTCUSDT\",\"k\":{\"c\":\"invalid_price\"}}",
  "failed_at": "2026-11-15T09:00:00.052000Z"
}
```

