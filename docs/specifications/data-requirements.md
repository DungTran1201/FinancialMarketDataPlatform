# Data Requirements Specification

## 1. Document Purpose

This specification defines the functional, data, integration, and analytical requirements for the **Real-time Financial Market Data Platform**. It explicitly separates confirmed requirements (derived from product objectives and architecture constraints) from baseline operational assumptions and unresolved questions requiring empirical benchmarking.

---

## 2. Requirements Classification

### 2.1. Confirmed Functional Requirements (FR)

| ID | Category | Requirement | Priority |
|---|---|---|---|
| **FR-01** | Ingestion (Streaming) | Collect real-time market events (Ticker, Trade, Kline/OHLCV, Order Book Top-of-Book / Diff Depth, Market Statistics) from Binance WebSocket API. | Mandatory |
| **FR-02** | Ingestion (Historical) | Collect and synchronize historical market data (Klines, Aggregated Trades, Exchange Info) from Binance REST API, supporting scheduled syncs and deterministic backfill ranges. | Mandatory |
| **FR-03** | Multi-Provider Extensibility | Normalize incoming provider-specific payloads into canonical platform event envelopes so additional exchanges/providers can be added without modifying downstream storage, analytics, or serving layers. | Mandatory |
| **FR-04** | Hot Data Serving | Serve low-latency latest prices and real-time market snapshots via REST and WebSocket endpoints without querying analytical or transactional databases on the hot path. | Mandatory |
| **FR-05** | Historical & Analytical Serving | Support high-performance time-series queries over historical candles, trades, order book snapshots, and pre-aggregated market statistics. | Mandatory |
| **FR-06** | Lakehouse Medallion Storage | Persist raw immutable events (Bronze), deduplicated and standardized datasets (Silver), and curated business/analytical models (Gold) in an Apache Iceberg + Parquet Lakehouse over MinIO. | Mandatory |
| **FR-07** | Data Quality & Lineage | Enforce schema validation at ingestion, deterministic deduplication in streaming/batch pipelines, and automated Great Expectations assertions across Lakehouse and OLAP layers. | Mandatory |
| **FR-08** | BI & Visualization | Expose curated analytical datasets in ClickHouse to Apache Superset for interactive dashboards and market surveillance views. | Mandatory |
| **FR-09** | Agentic Intelligence | Provide an isolated AI Agent service (LangGraph) capable of executing deterministic quantitative tools, investigating market/data anomalies, and generating structured evidence-backed reports. | Mandatory |
| **FR-10** | Platform Control & Governance | Manage users, RBAC roles, ingestion symbol subscriptions, backfill job states, and audit logs in PostgreSQL. | Mandatory |

---

## 3. Data Source & Workload Characteristics

### 3.1. Primary Data Source: Binance Spot (Initial Scope)

| Stream / Endpoint Type | Protocol | Binance Stream / Endpoint | Canonical Entity | Expected Event Cadence | Ordering & Consistency Requirement |
|---|---|---|---|---|---|
| **Individual Trade / AggTrade** | WebSocket (`wss://stream.binance.com:9443/ws`) | `<symbol>@trade` or `<symbol>@aggTrade` | `MarketTradeEvent` | 10–500+ events/sec per active pair | Strict ordering per `(provider, symbol)` by `exchange_event_time` and `trade_id`. |
| **Kline / Candlestick** | WebSocket | `<symbol>@kline_<interval>` (`1m`, `5m`, `1h`, `1d`) | `MarketKlineEvent` | 1 update every 1–2s per symbol/interval | Upsert/latest state within open window; immutable upon `is_closed = true`. |
| **24hr Mini / Full Ticker** | WebSocket | `<symbol>@ticker` / `!ticker@arr` | `MarketTickerEvent` | 1 update/sec per symbol | Latest-value semantics guarded by `exchange_event_time`. |
| **Order Book Depth** | WebSocket + REST Snapshot | `<symbol>@depth20@100ms` or `<symbol>@bookTicker` | `OrderBookSnapshotEvent` | 1–10 updates/sec per symbol | Sequence continuity verified via `first_update_id` (`U`) and `final_update_id` (`u`). |
| **Historical Klines** | REST (`https://api.binance.com/api/v3/klines`) | `GET /api/v3/klines` | `MarketKlineRecord` | Batch paginated (up to 1000 rows/request) | Idempotent range backfill keyed by `(provider, symbol, interval, open_time)`. |
| **Exchange Metadata** | REST (`https://api.binance.com/api/v3/exchangeInfo`) | `GET /api/v3/exchangeInfo` | `InstrumentMetadata` | Periodic refresh (hourly/daily) | Transactional upsert in PostgreSQL catalog. |

### 3.2. Data Volume & Sizing Assumptions (Local / Constrained Baseline)

Because production symbol universe size is not fixed in the initial prompt, the architecture defines a **Tier-1 Local Baseline Profile** (10–25 high-liquidity spot pairs, e.g., `BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`) and a **Tier-2 Scale Profile** (200+ pairs):

| Metric | Tier-1 Baseline (10–25 Symbols) | Tier-2 Expansion (200 Symbols) | Architectural Impact |
|---|---|---|---|
| **Ingest Event Rate** | ~200 – 1,500 events/sec | ~5,000 – 25,000 events/sec | Requires micro-batched asynchronous ClickHouse inserts (1s–5s or 1,000–10,000 rows) rather than row-by-row inserts. |
| **Raw Daily Uncompressed Volume** | ~0.5 – 3 GB / day | ~15 – 60 GB / day | Requires Parquet ZSTD compression in MinIO and TTL/tiering policies in ClickHouse. |
| **Hot State Footprint (Redis)** | < 50 MB | < 500 MB | Easily fits in memory with strict key schemas and bounded TTLs; no historical tick storage in Redis. |

---

## 4. Data Freshness, Completeness, and Quality Requirements

| Data Path | Target End-to-End Freshness | Delivery Guarantee | Deduplication & Ordering Strategy |
|---|---|---|---|
| **Hot Path (Redis)** | $\le 500\text{ ms}$ from collector receipt | At-least-once ingestion; idempotent monotonic state update | Lua / conditional check ensuring `incoming.exchange_event_time >= stored.exchange_event_time`. |
| **Analytics Path (ClickHouse)** | $1\text{s} - 5\text{s}$ (micro-batch flush window) | At-least-once delivery with eventual deduplication | `ReplacingMergeTree(version)` keyed by natural event identifiers (`provider, symbol, trade_id` or `open_time`). |
| **Lakehouse Bronze (MinIO/Iceberg)** | $5\text{m} - 15\text{m}$ micro-batch or scheduled flush | Immutable append-only raw preservation | Partitioned by `(provider, event_type, ingestion_date)`; preserves exact raw payload and ingestion metadata. |
| **Lakehouse Silver (Iceberg)** | $15\text{m} - 1\text{h}$ scheduled batch | Deterministic ACID table state | PySpark merge/deduplicate over `(provider, symbol, event_id/timestamp)` + Great Expectations validation. |
| **Lakehouse Gold / dbt Marts** | $15\text{m} - 24\text{h}$ depending on model cadence | Reproducible analytical views/tables | Incremental dbt models over ClickHouse and/or Iceberg curated tables. |

---

## 5. Confirmed Requirements vs. Assumptions & Unresolved Decisions

| Item | Status | Current Baseline Decision | Validation / Finalization Action |
|---|---|---|---|
| **Initial Symbol Universe** | Assumption | Default configured to top 10 spot pairs (`BTCUSDT`, `ETHUSDT`, `SOLUSDT`, etc.) in `.env.example` and seed config. | Configurable dynamically via PostgreSQL `platform_config.monitored_symbols` table without code changes. |
| **Order Book Granularity** | Assumption | Use top-20 depth snapshots (`@depth20@100ms` / `@bookTicker`) initially rather than full L2 diff reconstruction for every tick. | Full L2 diff book reconstruction can be enabled per-symbol in a dedicated collector worker if sub-second market-making analytics are required. |
| **LLM Provider Selection** | Unresolved | Abstracted behind `LLMProviderPort` (`OpenAI` / `Anthropic` / `Gemini` / local `Ollama` compatible). | Operator supplies provider credentials via environment variables; Data Plane runs unaffected with zero LLM credentials. |
| **Historical Backfill Depth** | Assumption | Default initial backfill scope set to 90 days of `1m`/`1h`/`1d` klines for configured symbols. | Adjustable per Airflow DAG trigger parameters (`start_date`, `end_date`, `intervals`). |

