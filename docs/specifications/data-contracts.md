# Data Contracts & Event Schema Specification

## 1. Overview

All asynchronous communication across the Data Plane is governed by explicit, versioned **Data Contracts**. Producers (Collectors, Anomaly Detectors) must validate events before publishing to Apache Kafka, and Consumers (Hot Cache Updater, ClickHouse Sink, Lakehouse Archiver, Agent Worker) must validate schema compatibility and handle malformed payloads via Dead-Letter Topics (`*.dlq`).

---

## 2. Kafka Topic Topology & Partitioning Strategy

| Kafka Topic | Event Contract | Partition Key | Initial Partitions | Configured Retention (`topics-init.sh`) | Compaction | Primary Consumer Groups (`topics.yaml`) |
|---|---|---|---|---|---|---|
| `market.raw.trades.v1` | `MarketTradePayloadV1` | `{provider}:{symbol}` | 6 | `168 hours` (`7 days`) | `delete` | `cg.hot.redis.v1`, `cg.analytics.clickhouse.v1`, `cg.lakehouse.bronze.v1` (`PARTIALLY_IMPLEMENTED`) |
| `market.raw.klines.v1` | `MarketKlinePayloadV1` | `{provider}:{symbol}:{interval}` | 6 | `168 hours` (`7 days`) | `delete` | `cg.hot.redis.v1`, `cg.analytics.clickhouse.v1`, `cg.lakehouse.bronze.v1` (`PARTIALLY_IMPLEMENTED`) |
| `market.raw.tickers.v1` | Ticker payload dict | `{provider}:{symbol}` | 6 | `168 hours` (`7 days`) | `delete` | `cg.hot.redis.v1`, `cg.analytics.clickhouse.v1` |
| `market.raw.orderbook.v1` | Order book payload dict | `{provider}:{symbol}` | 6 | `168 hours` (`7 days`) | `delete` | `cg.hot.redis.v1`, `cg.analytics.clickhouse.v1`, `cg.lakehouse.bronze.v1` (`PARTIALLY_IMPLEMENTED`) |
| `market.anomalies.v1` | `MarketAnomalyEventV1` | `{provider}:{symbol}` | 3 | `720 hours` (`30 days`) | `delete` | `cg.agent.anomaly.v1` (`PLANNED`) |
| `market.dlq.v1` | `DeadLetterEnvelopeV1` | `{source_topic}:{symbol}` | 3 | `720 hours` (`30 days`) | `delete` | `cg.dlq.inspector.v1` *(trace/observability label only; manual/operator inspection)* |

### Partition Key Rationale
- Partitioning by `{provider}:{symbol}` guarantees **strict in-order delivery per trading pair** within a single Kafka partition while distributing load evenly across consumer group instances when multiple symbols are active.
- Never partition by random UUID or timestamp, as that destroys per-symbol sequence guarantees and causes out-of-order state overwrites.

---

## 3. Canonical JSON / Python Dataclass Event Schemas

> [!NOTE]
> Runtime event envelopes (`EventEnvelopeV1`, `MarketTradePayloadV1`, `MarketKlinePayloadV1`, `DeadLetterEnvelopeV1`) are implemented in `src/shared/contracts/events/market_events.py` as frozen Python `@dataclass(frozen=True, slots=True)` contracts enforcing `Decimal` financial invariants and timezone-aware UTC timestamps.

### 3.1. Common Envelope Contract (`EventEnvelopeV1`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "EventEnvelopeV1",
  "type": "object",
  "required": [
    "event_id",
    "schema_version",
    "provider",
    "symbol",
    "event_type",
    "exchange_event_time",
    "ingested_at",
    "payload"
  ],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "Deterministic UUIDv5 derived from natural key: uuid5(NAMESPACE, '{provider}:{event_type}:{symbol}:{natural_key}')"
    },
    "schema_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
      "const": "1.0.0"
    },
    "provider": {
      "type": "string",
      "enum": ["binance"]
    },
    "symbol": {
      "type": "string",
      "pattern": "^[A-Z0-9]{4,20}$"
    },
    "event_type": {
      "type": "string",
      "enum": ["trade", "kline", "ticker", "order_book", "anomaly"]
    },
    "exchange_event_time": {
      "type": "string",
      "format": "date-time",
      "description": "ISO-8601 UTC timestamp with millisecond precision"
    },
    "ingested_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO-8601 UTC timestamp when collector received event"
    },
    "sequence_id": {
      "type": "integer",
      "minimum": 0
    },
    "payload": {
      "type": "object"
    }
  },
  "additionalProperties": false
}
```

### 3.2. `MarketTradeEventV1` Payload (`market.raw.trades.v1`)

- **Natural Key for Deterministic `event_id`**: `{provider}:trade:{symbol}:{trade_id}`

```json
{
  "trade_id": 419283741,
  "price": "89420.50000000",
  "quantity": "0.12500000",
  "quote_volume": "11177.56250000",
  "trade_time": "2026-11-12T02:58:00.123Z",
  "buyer_order_id": 29182731,
  "seller_order_id": 29182739,
  "is_buyer_maker": false
}
```

### 3.3. `MarketKlineEventV1` Payload (`market.raw.klines.v1`)

- **Natural Key for Deterministic `event_id`**: `{provider}:kline:{symbol}:{interval}:{open_time_ms}:{exchange_event_time_ms}`
- **Natural Deduplication Key in Storage**: `(provider, symbol, interval, open_time)` keeping highest `exchange_event_time`.

```json
{
  "interval": "1m",
  "open_time": "2026-11-12T02:58:00.000Z",
  "close_time": "2026-11-12T02:58:59.999Z",
  "open_price": "89400.00000000",
  "high_price": "89455.20000000",
  "low_price": "89390.10000000",
  "close_price": "89420.50000000",
  "base_volume": "42.81900000",
  "quote_volume": "3829104.22100000",
  "trade_count": 1420,
  "taker_buy_base_volume": "24.11000000",
  "taker_buy_quote_volume": "2156019.55000000",
  "is_closed": false
}
```

### 3.4. `MarketTickerEventV1` Payload (`market.raw.tickers.v1`)

- **Natural Key for Deterministic `event_id`**: `{provider}:ticker:{symbol}:{exchange_event_time_ms}`

```json
{
  "last_price": "89420.50000000",
  "best_bid_price": "89420.40000000",
  "best_bid_qty": "2.45000000",
  "best_ask_price": "89420.50000000",
  "best_ask_qty": "1.12000000",
  "price_change_24h": "1820.50000000",
  "price_change_pct_24h": "2.078",
  "vwap_24h": "88610.12000000",
  "high_24h": "89900.00000000",
  "low_24h": "87250.00000000",
  "base_volume_24h": "31492.44100000",
  "quote_volume_24h": "2790548991.12000000",
  "trade_count_24h": 984120
}
```

### 3.5. `MarketAnomalyEventV1` Payload (`market.anomalies.v1`)

Emitted by deterministic threshold/statistical anomaly detectors when price return Z-score, volume spike, spread widening, or data staleness breaches configured thresholds.

```json
{
  "anomaly_id": "a7c9e112-84b1-4a39-9e1d-5b8d9a123456",
  "detector_name": "rolling_volatility_zscore_v1",
  "severity": "HIGH",
  "metric_name": "return_1m_zscore",
  "observed_value": "4.82",
  "threshold_value": "3.50",
  "window_start": "2026-11-12T02:00:00.000Z",
  "window_end": "2026-11-12T02:58:00.000Z",
  "dedup_window_key": "binance:BTCUSDT:rolling_volatility_zscore_v1:2026-11-12T02:55"
}
```

---

### 3.6. `DeadLetterEnvelopeV1` Payload (`market.dlq.v1`)

Runtime wrapper fields emitted when normalization/parsing fails (`src/shared/contracts/events/market_events.py`):
```json
{
  "dlq_id": "dlq-7c81a9f0-32b4-5d9e-bc41-89012a45d678",
  "source_provider": "binance",
  "source_stream": "market.raw.klines.v1",
  "error_type": "ValidationError",
  "error_message": "Kline invariant violated: high_price < low_price",
  "raw_payload": "{\"e\":\"kline\",\"s\":\"BTCUSDT\"}",
  "failed_at": "2026-11-15T09:00:00.052000Z"
}
```

---

## 4. Schema Evolution & Contract Governance Rules

1. **Backward Compatibility by Default**:
   - Minor version increments (`1.0.0` $\rightarrow$ `1.1.0`) may only add optional fields with sensible defaults.
   - Existing required fields must never be renamed, removed, or have their type changed within the same major version (`v1`).
2. **Breaking Changes Require Major Topic Version**:
   - Any breaking contract change requires introducing a new topic suffix (e.g., `market.raw.trades.v2`) and dual-publishing during consumer migration.
3. **Validation Gate at Producer & Consumer Boundaries**:
   - Normalizers validate payloads strictly (`EventEnvelopeV1`, `MarketTradePayloadV1`, `MarketKlinePayloadV1`) before publishing to Kafka.
   - If an exchange emits a malformed message, the ingestion boundary wraps it in `DeadLetterEnvelopeV1` and routes it to `market.dlq.v1` without crashing the collector loop.

