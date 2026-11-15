# 07 — Data Storage and Modeling Architecture

## 1. Polyglot Storage Responsibility Matrix

The platform operates four distinct storage engines, each engineered for a specific workload class (`ADR-003`):

| Storage Engine | Workload Class | Canonical Entities Owned | Retention Policy | Backup / Rebuild Strategy |
|---|---|---|---|---|
| **Redis 7** | Hot Ephemeral Key-Value & Pub/Sub | `market:v1:price:*`, `market:v1:snapshot:*`, `market:v1:orderbook:*`, `cache:v1:analytics:*`, `ratelimit:*` | Sliding TTL (`15s`–`300s`); `volatile-lru` eviction at `256MB` | Ephemeral; rebuilt live from Kafka or bypassed via ClickHouse fallback. |
| **ClickHouse** | Real-Time & Historical Columnar OLAP | `market_trades`, `market_klines`, `market_tickers`, `order_book_snapshots`, `mv_*`, `mart_*` | `market_trades` & `market_tickers`: `90 DAY` TTL (`01_schema.sql`); `market_klines`, `order_book_snapshots` & Marts: no DDL TTL (`5+ years` target) | Rebuilt from Iceberg Silver tables (`PLANNED` Airflow/Spark job) or ClickHouse native backup. |
| **MinIO + Parquet + Iceberg** | Medallion Lakehouse (Bronze / Silver / Gold) | `bronze.raw_*`, `silver.market_*`, `gold.fct_*` | Permanent archive (Bronze/Silver/Gold) with Iceberg snapshot expiration (`7 days` target); active v0.1 writes ZSTD Parquet + Iceberg v2 manifests to `.local_lakehouse` (MinIO buckets `lakehouse-*` provisioned) | S3 bucket replication / MinIO erasure coding (`PLANNED` multi-node target). |
| **PostgreSQL 16** | Transactional Control Plane & Agent State | `users`, `api_keys`, `monitored_instruments`, `ingestion_watermarks`, `backfill_jobs`, `agent_runs`, `agent_tool_invocations`, `audit_logs` | Permanent transactional history | Daily `pg_dump` / WAL archive to MinIO backup bucket (`PLANNED` automated cron). |

---

## 2. ClickHouse Physical Schema & Performance Design

ClickHouse tables are designed strictly around actual API, BI, and Agent query patterns (`WHERE provider = ? AND symbol = ? AND open_time BETWEEN ? AND ?`).

### 2.1. Base Table: `market_data.market_klines`
```sql
CREATE TABLE IF NOT EXISTS market_data.market_klines
(
    provider                LowCardinality(String),
    symbol                  LowCardinality(String),
    interval                LowCardinality(String),
    open_time               DateTime64(3, 'UTC'),
    close_time              DateTime64(3, 'UTC'),
    open_price              Decimal128(18),
    high_price              Decimal128(18),
    low_price               Decimal128(18),
    close_price             Decimal128(18),
    base_volume             Decimal128(18),
    quote_volume            Decimal128(18),
    trade_count             UInt64,
    taker_buy_base_volume   Decimal128(18),
    taker_buy_quote_volume  Decimal128(18),
    is_closed               Bool,
    exchange_event_time     DateTime64(3, 'UTC'),
    ingested_at             DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(exchange_event_time)
PARTITION BY toYYYYMM(open_time)
ORDER BY (provider, symbol, interval, open_time)
SETTINGS index_granularity = 8192;
```
- **Why `ReplacingMergeTree(exchange_event_time)`**: Streaming klines emit updates every 1–2s within an open candle window and may be re-delivered during Kafka consumer restarts. Keying by `(provider, symbol, interval, open_time)` and versioning by `exchange_event_time` guarantees that background merges always retain the latest state (including the finalized `is_closed = true` candle).
- **Why `ORDER BY (provider, symbol, interval, open_time)`**: Matches 100% of candle queries, enabling sparse primary index pruning to read only the exact 8,192-row granules covering the requested symbol, interval, and time window.
- **No High-Cardinality Secondary Indexes**: Avoids skip indexes on high-cardinality fields like `price` or `trade_id`, which bloat disk I/O during merges without accelerating time-range scans.

### 2.2. Base Table: `market_data.market_trades`
```sql
CREATE TABLE IF NOT EXISTS market_data.market_trades
(
    provider             LowCardinality(String),
    symbol               LowCardinality(String),
    trade_id             UInt64,
    price                Decimal128(18),
    quantity             Decimal128(18),
    quote_volume         Decimal128(18),
    buyer_order_id       UInt64,
    seller_order_id      UInt64,
    is_buyer_maker       Bool,
    trade_time           DateTime64(3, 'UTC'),
    exchange_event_time  DateTime64(3, 'UTC'),
    ingested_at          DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(ingested_at)
PARTITION BY toYYYYMM(trade_time)
ORDER BY (provider, symbol, trade_time, trade_id)
TTL toDateTime(trade_time) + INTERVAL 90 DAY DELETE
SETTINGS index_granularity = 8192;
```

### 2.3. Materialized View: `market_data.mv_hourly_trade_stats`
To avoid scanning millions of raw trade rows during API or Superset dashboard queries, an incremental `AggregatingMergeTree` target table and Materialized View pre-aggregate hourly trade metrics:
```sql
CREATE TABLE IF NOT EXISTS market_data.hourly_trade_stats
(
    provider          LowCardinality(String),
    symbol            LowCardinality(String),
    hour_bucket       DateTime('UTC'),
    open_price        AggregateFunction(argMin, Decimal128(18), DateTime64(3, 'UTC')),
    high_price        SimpleAggregateFunction(max, Decimal128(18)),
    low_price         SimpleAggregateFunction(min, Decimal128(18)),
    close_price       AggregateFunction(argMax, Decimal128(18), DateTime64(3, 'UTC')),
    base_volume       SimpleAggregateFunction(sum, Decimal128(18)),
    quote_volume      SimpleAggregateFunction(sum, Decimal128(18)),
    trade_count       SimpleAggregateFunction(sum, UInt64)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(hour_bucket)
ORDER BY (provider, symbol, hour_bucket);
```

---

## 3. Lakehouse Medallion Modeling (MinIO + Parquet + Iceberg)

### 3.1. Partitioning & File Sizing Rules
- **Bronze (`lakehouse.bronze.raw_*`)**:
  - Active v0.1 writes immutable ZSTD-compressed Apache Parquet files partitioned by `bronze/{event_type}/provider={p}/ingestion_date={YYYY-MM-DD}` (`BronzeParquetArchiver` in `src/lakehouse/bronze/archiver.py`). Target MinIO object storage buckets (`lakehouse-bronze`, `lakehouse-silver`, `lakehouse-gold`, `lakehouse-checkpoints`) are provisioned via `deploy/object-storage/init-buckets.sh`.
- **Silver (`silver.market_trades`, `silver.market_klines`, `silver.order_book_snapshots`)**:
  - Active v0.1 executes natural-key deduplication and ZSTD Parquet + Iceberg v2 snapshot manifest generation via `SilverLakehouseMergeEngine` (`src/lakehouse/silver/merge_engine.py`). PySpark `MERGE INTO` against hidden-partitioned MinIO Iceberg tables is the `PLANNED` distributed batch target (`deploy/iceberg/catalog-config.yaml`).
- **Gold (`gold.*` Parquet Active; dbt Marts `PLANNED`)**:
  - `gold.fct_daily_market_summary` (`IMPLEMENTED` in `GoldLayerMartEngine`): Daily OHLCV, VWAP, dollar volume, and taker buy volume per symbol.
  - `gold.fct_realized_volatility` (`IMPLEMENTED` in `GoldLayerMartEngine`): Close-to-close realized volatility per symbol/interval.
  - `gold.fct_orderbook_liquidity` (`IMPLEMENTED` in `GoldLayerMartEngine`): Top-N bid/ask spread, mid-price, and cumulative depth summary.
  - `gold.fct_cross_asset_correlations` (`PLANNED` target mart; correlation calculation is currently served on-demand by `/api/v1/analytics/correlations` and `calculate_correlation`).

---

## 4. PostgreSQL Control Plane Schema Design

PostgreSQL stores strictly bounded relational control and state entities:
- **Primary Keys**: UUIDv4/v7 (`UUID PRIMARY KEY`).
- **Indexes**:
  - `UNIQUE INDEX idx_monitored_instruments_provider_symbol ON monitored_instruments (provider, symbol)`
  - `UNIQUE INDEX idx_watermarks_natural ON ingestion_watermarks (provider, symbol, dataset)`
  - `INDEX idx_agent_runs_status_created ON agent_runs (status, started_at DESC)`
  - `INDEX idx_agent_tools_run_id ON agent_tool_invocations (run_id, started_at ASC)`
- **Transactional Boundaries**: Each Command Handler executes within an explicit `async with session.begin():` unit-of-work transaction. External network calls (Kafka, Redis, LLM) are never executed while holding an open PostgreSQL transaction lock.

