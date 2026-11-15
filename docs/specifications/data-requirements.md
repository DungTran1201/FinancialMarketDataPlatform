# Data Requirements Specification

## 1. Document Purpose

This specification defines the functional, data, integration, and analytical requirements for the **Real-time Financial Market Data Platform**. It explicitly separates confirmed requirements (derived from product objectives and architecture constraints) from baseline operational assumptions and unresolved questions requiring empirical benchmarking.

---

## 2. Requirements Classification

### 2.1. Confirmed Functional Requirements (FR)

| ID | Category | Requirement | Priority | Implementation Status (`models/requirements/requirements.yaml`) |
|---|---|---|---|---|
| **FR-01** | Ingestion (Streaming) | Collect real-time market events (Ticker, Trade, Kline/OHLCV, Order Book Depth) from Binance WebSocket API. | Mandatory | `PARTIALLY_IMPLEMENTED` *(adapters + ingest API implemented; standalone `collector-ws` CLI stub)* |
| **FR-02** | Ingestion (Historical) | Collect and synchronize historical market data (Klines, Aggregated Trades, Exchange Info) from Binance REST API with deterministic backfill ranges. | Mandatory | `PARTIALLY_IMPLEMENTED` *(REST client, watermarks & API implemented; standalone `collector-rest` CLI & Airflow `PLANNED`)* |
| **FR-03** | Multi-Provider Canonical Normalization | Normalize incoming provider-specific payloads into canonical `EventEnvelopeV1` envelopes with UUIDv5 idempotency keys. | Mandatory | `IMPLEMENTED` |
| **FR-04** | Low-Latency Hot Data Serving | Serve low-latency latest prices, snapshots, and observability streams without blocking on analytical databases on the hot path. | Mandatory | `IMPLEMENTED` *(REST + Observability WS/SSE implemented; `WS /ws/v1/market/stream` `PLANNED`)* |
| **FR-05** | Historical & Analytical Serving | Support high-performance bounded time-series queries over historical candles, trades, correlations, and market statistics. | Mandatory | `IMPLEMENTED` |
| **FR-06** | Lakehouse Medallion Storage | Persist Bronze, Silver, and Gold datasets in Parquet and Iceberg v2 manifests (targeting MinIO object storage). | Mandatory | `PARTIALLY_IMPLEMENTED` *(local `.local_lakehouse` Parquet + Iceberg v2 manifests implemented; MinIO S3 transport & distributed catalog `PLANNED`)* |
| **FR-07** | Data Quality & Lineage Enforcement | Enforce schema validation at ingestion, deterministic deduplication, and `Decimal` quality assertions via `DataQualityGateEngine` (`DQ-KLINE-001..005`, `DQ-TRADE-001..003`; Great Expectations runtime `PLANNED`). | Mandatory | `PARTIALLY_IMPLEMENTED` |
| **FR-08** | BI & Visualization | Expose curated analytical datasets in ClickHouse to Apache Superset for interactive dashboards. | Mandatory | `PARTIALLY_IMPLEMENTED` *(ClickHouse DDL & `bi` Compose profile exist; automated Gold->CH sync & prebuilt dashboards `PLANNED`)* |
| **FR-09** | Agentic Intelligence | Provide an isolated AI Agent orchestrator (5-node LangGraph) executing deterministic tools via `ControlledToolGateway` (`10` tools). | Mandatory | `PARTIALLY_IMPLEMENTED` *(on-demand API & 5-node graph implemented; standalone `agent-worker` Kafka loop `PLANNED`)* |
| **FR-10** | Platform Control & Governance | Manage auth tokens/API keys, monitored instruments, watermark state, telemetry, and audit logs across PostgreSQL and control-plane endpoints. | Mandatory | `PARTIALLY_IMPLEMENTED` *(IAM endpoints & observability active; per-route domain RBAC `Depends` guards `PLANNED` / `PROP-APP-004`)* |

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
| **Lakehouse Bronze (MinIO / Local Parquet)** | $5\text{m} - 15\text{m}$ micro-batch or scheduled flush | Immutable append-only raw preservation | Partitioned by `(provider, event_type, ingestion_date)`; active v0.1 uses `BronzeParquetArchiver` to `.local_lakehouse`, MinIO `lakehouse-bronze` bucket provisioned. |
| **Lakehouse Silver (Iceberg)** | $15\text{m} - 1\text{h}$ scheduled batch | Deterministic ACID table state | Active v0.1 uses `SilverLakehouseMergeEngine` + `DataQualityGateEngine`; distributed PySpark `MERGE INTO` + Great Expectations are `PLANNED` targets. |
| **Lakehouse Gold / dbt Marts** | $15\text{m} - 24\text{h}$ depending on model cadence | Reproducible analytical views/tables | Active v0.1 computes Gold marts via `GoldLayerMartEngine`; `dbt` SQL execution over Iceberg/ClickHouse is `PLANNED`. |

---

## 5. Confirmed Requirements vs. Assumptions & Unresolved Decisions

| Item | Status | Current Baseline Decision | Validation / Finalization Action |
|---|---|---|---|
| **Initial Symbol Universe** | Assumption | Default configured pairs (`BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, etc.) in `.env.example` / config. | Configurable dynamically via PostgreSQL `monitored_instruments` table & `PUT /api/v1/catalog/instruments/{symbol}`. |
| **Order Book Granularity** | Assumption | Use top-20 depth snapshots (`@depth20@100ms` / `@bookTicker`) initially rather than full L2 diff reconstruction for every tick. | Full L2 diff book reconstruction can be enabled per-symbol in a dedicated collector worker if sub-second market-making analytics are required. |
| **LLM Provider Selection** | Unresolved | Abstracted behind `LLMProviderPort` (`OpenAI` / `Anthropic` / `Gemini` / local `Ollama` / `mock` compatible). | Operator supplies provider credentials via environment variables; Data Plane runs unaffected with zero LLM credentials. |
| **Historical Backfill Depth** | Assumption | Default initial backfill scope target set to 90 days of `1m`/`1h`/`1d` klines for configured symbols. | Adjustable per backfill request or `PLANNED` Airflow DAG trigger parameters (`start_date`, `end_date`, `intervals`). |

