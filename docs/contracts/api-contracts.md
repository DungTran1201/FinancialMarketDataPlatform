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

Authoritative specification: `models/api/api.yaml` and `docs/specifications/api-specification.md`.

### 1.1. Core Market & Historical Endpoints

| Method | Route | Description | Auth Required | Backing Microservice |
|---|---|---|---|---|
| `GET` | `/health` | Gateway healthcheck & downstream service status | No | `svc-api-gateway:8000` |
| `GET` | `/metrics` | Prometheus OpenMetrics telemetry endpoint | No | `svc-api-gateway:8000` |
| `GET` | `/api/v1/market/prices` | Latest spot prices across all supported trading pairs | Optional | `svc-market-hot:8001` |
| `GET` | `/api/v1/market/orderbook/{symbol}` | Top-20 level-2 order book depth from Redis hot state | Optional | `svc-market-hot:8001` |
| `GET` | `/api/v1/market/ticker/24h` | 24-hour rolling statistics (high, low, volume, VWAP) | Optional | `svc-market-hot:8001` |
| `GET` | `/api/v1/historical/klines` | Historical OHLCV candles from ClickHouse with pagination | Yes | `svc-historical-backfill:8002` |
| `POST` | `/api/v1/historical/backfill` | Trigger backfill job for a specified time range | Yes (Admin) | `svc-historical-backfill:8002` |
| `GET` | `/api/v1/analytics/volatility` | Realized volatility & statistical quant calculations | Yes | `svc-analytics-quant:8003` |
| `GET` | `/api/v1/analytics/correlations` | Cross-instrument Pearson correlation matrix | Yes | `svc-analytics-quant:8003` |

### 1.2. Observability & Data Plane Endpoints

| Method | Route | Description | Backing Microservice |
|---|---|---|---|
| `GET` | `/api/v1/observability/data-flow` | Complete live pipeline flow, stage metrics & latency | `svc-data-plane-v01:8007` |
| `GET` | `/api/v1/observability/pipeline-health`| Component health, active lag, and error rates | `svc-data-plane-v01:8007` |
| `GET` | `/api/v1/observability/stream/events` | Server-Sent Events (SSE) stream of real-time events | `svc-api-gateway:8000` |
| `GET` | `/api/v1/microservices/topology` | Runtime microservices topology & container process status | `svc-api-gateway:8000` |

---

## 2. Real-Time Streaming Protocols

### 2.1. WebSocket Stream Channels (`ws://localhost:8000/ws/market`)
Clients connect via WebSocket and submit subscription frames:
```json
{
  "action": "subscribe",
  "channels": ["trades:BTCUSDT", "orderbook:BTCUSDT", "ticker:BTCUSDT"]
}
```
Market update broadcast envelope:
```json
{
  "channel": "trades:BTCUSDT",
  "timestamp": 1731638400000,
  "data": {
    "symbol": "BTCUSDT",
    "price": "92450.50",
    "quantity": "0.1540",
    "side": "buy",
    "trade_id": "84729103"
  }
}
```

### 2.2. Server-Sent Events (SSE) Pipeline Stream (`GET /api/v1/observability/stream/events`)
Streams live event metrics directly to the Frontend observatory without polling:
```text
event: pipeline_metrics
data: {"ingested_total": 45200, "processed_total": 45198, "throughput_eps": 145.2, "latency_ms": 38.4, "consumer_lag": 2}

event: stage_latency
data: {"stage": "LakehouseArchiver", "p95_latency_ms": 12.4, "status": "HEALTHY"}
```

---

## 3. Kafka Event Envelope Specification (`models/data-platform/events.yaml`)

Every message published to Kafka follows the versioned canonical envelope:
```json
{
  "schema_version": "1.0",
  "event_id": "evt-84729103-91284",
  "event_type": "MARKET_KLINE",
  "source_provider": "binance",
  "symbol": "BTCUSDT",
  "occurred_at": "2026-11-15T09:00:00.000Z",
  "ingested_at": "2026-11-15T09:00:00.045Z",
  "payload": {
    "open": "92100.00",
    "high": "92550.00",
    "low": "92050.00",
    "close": "92450.50",
    "volume": "142.845",
    "trades_count": 3412
  }
}
```

