# Data Dictionary Specification

## 1. Overview

This document defines the canonical data entities, field types, precision rules, and storage mappings across the platform's four storage engines:
1. **Redis** (Hot State Cache)
2. **ClickHouse** (Real-time & Historical OLAP)
3. **MinIO / Apache Iceberg** (Bronze, Silver, Gold Lakehouse)
4. **PostgreSQL** (Control Plane, Metadata, Users, and Agent State)

### Financial Precision Rule
- All monetary prices, quantities, and volumes in canonical schemas use **exact decimal representations** (`Decimal(38, 18)` in ClickHouse/Iceberg, `NUMERIC(38, 18)` in PostgreSQL, and string-encoded decimals in JSON/Redis) to prevent IEEE-754 floating-point rounding errors.
- All timestamps are normalized to **UTC** with millisecond or microsecond precision (`DateTime64(3, 'UTC')` or `TIMESTAMPTZ`).

---

## 2. Core Market Data Entities

### 2.1. Canonical Event Envelope Metadata (All Streaming Events)

Every event published to Kafka and persisted to Bronze/Silver carries standard envelope attributes:

| Field Name | Logical Type | Nullable | Description |
|---|---|---|---|
| `event_id` | `UUID` / `String` | No | Deterministic UUIDv5 derived from `(provider, event_type, symbol, natural_key)` for idempotency. |
| `schema_version` | `String` | No | Semantic version of the event contract (e.g., `"1.0.0"`). |
| `provider` | `LowCardinality(String)` | No | Source provider identifier (e.g., `"binance"`). |
| `symbol` | `LowCardinality(String)` | No | Canonical normalized instrument symbol (e.g., `"BTCUSDT"`). |
| `event_type` | `LowCardinality(String)` | No | Canonical type: `trade`, `ticker`, `kline`, `order_book`, `market_stats`. |
| `exchange_event_time` | `DateTime64(3, 'UTC')` | No | Timestamp emitted by the source exchange (UTC). |
| `ingested_at` | `DateTime64(3, 'UTC')` | No | Timestamp when the platform collector received the payload (UTC). |
| `sequence_id` | `UInt64` | Yes | Exchange-provided monotonic sequence number (`trade_id`, `update_id`, etc.). |

---

### 2.2. Entity: `market_trades` (Trades / AggTrades)

Represents individual executed market trades or aggregated trade ticks.

| Field Name | ClickHouse Type | Iceberg / Parquet Type | Nullable | Description |
|---|---|---|---|---|
| `provider` | `LowCardinality(String)` | `string` | No | Data source provider (`binance`). |
| `symbol` | `LowCardinality(String)` | `string` | No | Trading pair (`BTCUSDT`). |
| `trade_id` | `UInt64` | `long` | No | Exchange unique trade ID per symbol. |
| `price` | `Decimal128(18)` | `decimal(38, 18)` | No | Execution price. |
| `quantity` | `Decimal128(18)` | `decimal(38, 18)` | No | Executed base asset quantity. |
| `quote_volume` | `Decimal128(18)` | `decimal(38, 18)` | No | Derived `price * quantity` in quote asset. |
| `buyer_order_id` | `UInt64` | `long` | Yes | Exchange buyer order identifier. |
| `seller_order_id` | `UInt64` | `long` | Yes | Exchange seller order identifier. |
| `is_buyer_maker` | `Bool` | `boolean` | No | `true` if buyer was the resting limit order maker (sell aggressor). |
| `trade_time` | `DateTime64(3, 'UTC')` | `timestamp_tz` | No | Exchange execution timestamp. |
| `exchange_event_time` | `DateTime64(3, 'UTC')` | `timestamp_tz` | No | Exchange event emission timestamp. |
| `ingested_at` | `DateTime64(3, 'UTC')` | `timestamp_tz` | No | Collector ingestion timestamp (used as `ReplacingMergeTree` version). |

---

### 2.3. Entity: `market_klines` (Candlestick / OHLCV)

Represents time-bucketed OHLCV intervals (`1m`, `5m`, `15m`, `1h`, `4h`, `1d`).

| Field Name | ClickHouse Type | Iceberg / Parquet Type | Nullable | Description |
|---|---|---|---|---|
| `provider` | `LowCardinality(String)` | `string` | No | Exchange identifier (`binance`). |
| `symbol` | `LowCardinality(String)` | `string` | No | Trading pair (`BTCUSDT`). |
| `interval` | `LowCardinality(String)` | `string` | No | Candle interval (`1m`, `5m`, `15m`, `1h`, `4h`, `1d`). |
| `open_time` | `DateTime64(3, 'UTC')` | `timestamp_tz` | No | Candle window start timestamp (inclusive). |
| `close_time` | `DateTime64(3, 'UTC')` | `timestamp_tz` | No | Candle window end timestamp (inclusive). |
| `open_price` | `Decimal128(18)` | `decimal(38, 18)` | No | Opening price in interval. |
| `high_price` | `Decimal128(18)` | `decimal(38, 18)` | No | Highest price in interval. |
| `low_price` | `Decimal128(18)` | `decimal(38, 18)` | No | Lowest price in interval. |
| `close_price` | `Decimal128(18)` | `decimal(38, 18)` | No | Closing (or latest) price in interval. |
| `base_volume` | `Decimal128(18)` | `decimal(38, 18)` | No | Cumulative traded base asset volume. |
| `quote_volume` | `Decimal128(18)` | `decimal(38, 18)` | No | Cumulative traded quote asset volume. |
| `trade_count` | `UInt64` | `long` | No | Number of trades executed during the candle window. |
| `taker_buy_base_volume` | `Decimal128(18)` | `decimal(38, 18)` | No | Base volume initiated by taker buy orders. |
| `taker_buy_quote_volume` | `Decimal128(18)` | `decimal(38, 18)` | No | Quote volume initiated by taker buy orders. |
| `is_closed` | `Bool` | `boolean` | No | Whether the candle interval has finalized. |
| `exchange_event_time` | `DateTime64(3, 'UTC')` | `timestamp_tz` | No | Exchange event emission timestamp (used as deduplication version). |
| `ingested_at` | `DateTime64(3, 'UTC')` | `timestamp_tz` | No | Platform ingestion timestamp. |

---

### 2.4. Entity: `market_tickers` (24h Rolling Market Statistics & Best Bid/Ask)

| Field Name | ClickHouse Type | Redis Hash Field | Nullable | Description |
|---|---|---|---|---|
| `provider` | `LowCardinality(String)` | Key segment | No | Source provider (`binance`). |
| `symbol` | `LowCardinality(String)` | Key segment | No | Trading pair (`BTCUSDT`). |
| `last_price` | `Decimal128(18)` | `last_price` (str) | No | Latest traded price. |
| `best_bid_price` | `Decimal128(18)` | `best_bid_price` (str) | No | Current highest bid price. |
| `best_bid_qty` | `Decimal128(18)` | `best_bid_qty` (str) | No | Quantity available at best bid. |
| `best_ask_price` | `Decimal128(18)` | `best_ask_price` (str) | No | Current lowest ask price. |
| `best_ask_qty` | `Decimal128(18)` | `best_ask_qty` (str) | No | Quantity available at best ask. |
| `price_change_24h` | `Decimal128(18)` | `price_change_24h` (str) | No | Absolute 24h price change. |
| `price_change_pct_24h` | `Decimal64(6)` | `price_change_pct_24h` (str) | No | Percentage 24h price change. |
| `vwap_24h` | `Decimal128(18)` | `vwap_24h` (str) | No | 24h Volume Weighted Average Price. |
| `high_24h` | `Decimal128(18)` | `high_24h` (str) | No | 24h highest price. |
| `low_24h` | `Decimal128(18)` | `low_24h` (str) | No | 24h lowest price. |
| `base_volume_24h` | `Decimal128(18)` | `base_volume_24h` (str) | No | 24h total base volume. |
| `quote_volume_24h` | `Decimal128(18)` | `quote_volume_24h` (str) | No | 24h total quote volume. |
| `trade_count_24h` | `UInt64` | `trade_count_24h` (str) | No | 24h total trade count. |
| `exchange_event_time` | `DateTime64(3, 'UTC')` | `exchange_event_time_ms` | No | Exchange event timestamp. |
| `ingested_at` | `DateTime64(3, 'UTC')` | `ingested_at_ms` | No | Platform ingestion timestamp. |

---

### 2.5. Entity: `order_book_snapshots` (Top-N Depth Snapshot)

| Field Name | ClickHouse Type | Iceberg / Parquet Type | Nullable | Description |
|---|---|---|---|---|
| `provider` | `LowCardinality(String)` | `string` | No | Source provider (`binance`). |
| `symbol` | `LowCardinality(String)` | `string` | No | Trading pair (`BTCUSDT`). |
| `last_update_id` | `UInt64` | `long` | No | Exchange order book sequence ID (`lastUpdateId`). |
| `bids_price` | `Array(Decimal128(18))` | `list<decimal(38,18)>` | No | Ordered array of bid prices (highest to lowest). |
| `bids_quantity` | `Array(Decimal128(18))` | `list<decimal(38,18)>` | No | Corresponding bid quantities. |
| `asks_price` | `Array(Decimal128(18))` | `list<decimal(38,18)>` | No | Ordered array of ask prices (lowest to highest). |
| `asks_quantity` | `Array(Decimal128(18))` | `list<decimal(38,18)>` | No | Corresponding ask quantities. |
| `mid_price` | `Decimal128(18)` | `decimal(38, 18)` | No | Derived `(best_bid + best_ask) / 2`. |
| `spread_bps` | `Decimal64(6)` | `decimal(18, 6)` | No | Derived bid-ask spread in basis points. |
| `imbalance_top5` | `Decimal64(6)` | `decimal(18, 6)` | No | Top-5 level order book volume imbalance ratio `[-1, 1]`. |
| `exchange_event_time` | `DateTime64(3, 'UTC')` | `timestamp_tz` | No | Snapshot timestamp. |
| `ingested_at` | `DateTime64(3, 'UTC')` | `timestamp_tz` | No | Collector ingestion timestamp. |

---

## 3. Control Plane & Intelligence Plane Entities (PostgreSQL)

### 3.1. Table: `users` & `api_keys` (Authentication & RBAC)

| Column | PostgreSQL Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Unique user ID. |
| `email` | `VARCHAR(255)` | `UNIQUE NOT NULL` | User login email. |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | Argon2id password hash. |
| `role` | `VARCHAR(32)` | `NOT NULL` | Enum: `admin`, `operator`, `analyst`, `viewer`, `service`. |
| `is_active` | `BOOLEAN` | `NOT NULL DEFAULT TRUE` | Account status flag. |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL DEFAULT NOW()` | Creation timestamp. |

### 3.2. Table: `monitored_instruments` (Platform Configuration)

| Column | PostgreSQL Type | Constraints | Description |
|---|---|---|---|
| `instrument_id` | `UUID` | `PRIMARY KEY` | Surrogate key. |
| `provider` | `VARCHAR(32)` | `NOT NULL` | Data source (`binance`). |
| `symbol` | `VARCHAR(32)` | `NOT NULL` | Canonical symbol (`BTCUSDT`). |
| `base_asset` | `VARCHAR(16)` | `NOT NULL` | Base asset (`BTC`). |
| `quote_asset` | `VARCHAR(16)` | `NOT NULL` | Quote asset (`USDT`). |
| `status` | `VARCHAR(32)` | `NOT NULL` | `TRADING`, `HALTED`, `INACTIVE`. |
| `enabled_streams` | `JSONB` | `NOT NULL` | Enabled streams (`["trade", "kline_1m", "ticker", "depth20"]`). |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | Last configuration change timestamp. |

### 3.3. Table: `ingestion_watermarks` (Backfill & Sync State)

| Column | PostgreSQL Type | Constraints | Description |
|---|---|---|---|
| `watermark_id` | `UUID` | `PRIMARY KEY` | Unique record ID. |
| `provider` | `VARCHAR(32)` | `NOT NULL` | Provider name. |
| `symbol` | `VARCHAR(32)` | `NOT NULL` | Symbol name. |
| `dataset` | `VARCHAR(64)` | `NOT NULL` | Dataset (`klines_1m`, `klines_1h`, `agg_trades`). |
| `last_synced_timestamp` | `TIMESTAMPTZ` | `NOT NULL` | Latest verified contiguous historical timestamp synced. |
| `status` | `VARCHAR(32)` | `NOT NULL` | `IDLE`, `RUNNING`, `FAILED`, `COMPLETED`. |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL` | Last watermark update timestamp. |

### 3.4. Table: `agent_runs` & `agent_tool_invocations` (Intelligence Plane State)

| Table | Column | PostgreSQL Type | Description |
|---|---|---|---|
| `agent_runs` | `run_id` | `UUID PRIMARY KEY` | Unique execution workflow ID. |
| `agent_runs` | `trigger_mode` | `VARCHAR(32) NOT NULL` | `ON_DEMAND` or `EVENT_TRIGGERED`. |
| `agent_runs` | `requested_by` | `UUID NULL` | User ID (or `NULL` for anomaly trigger). |
| `agent_runs` | `status` | `VARCHAR(32) NOT NULL` | `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`. |
| `agent_runs` | `prompt_summary` | `TEXT NOT NULL` | User query or anomaly alert descriptor. |
| `agent_runs` | `structured_report` | `JSONB NULL` | Validated output report with data provenance citations. |
| `agent_runs` | `token_usage` | `JSONB NOT NULL` | Prompt, completion, and total token metrics. |
| `agent_runs` | `started_at` / `completed_at` | `TIMESTAMPTZ` | Execution lifecycle timestamps. |
| `agent_tool_invocations` | `invocation_id` | `UUID PRIMARY KEY` | Unique tool call audit record. |
| `agent_tool_invocations` | `run_id` | `UUID REFERENCES agent_runs(run_id)` | Parent workflow run. |
| `agent_tool_invocations` | `tool_name` | `VARCHAR(64) NOT NULL` | Deterministic tool executed (e.g., `calculate_volatility`). |
| `agent_tool_invocations` | `input_params` | `JSONB NOT NULL` | Validated tool input parameters. |
| `agent_tool_invocations` | `output_metadata` | `JSONB NOT NULL` | Data source, time range, row count, execution time (ms). |
| `agent_tool_invocations` | `status` | `VARCHAR(32) NOT NULL` | `SUCCESS`, `TIMEOUT`, `VALIDATION_ERROR`, `SOURCE_ERROR`. |

