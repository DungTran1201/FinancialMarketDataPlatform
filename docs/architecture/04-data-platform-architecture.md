# 04 — Data Platform Architecture

## 1. Data Architecture Overview: Three Workload-Optimized Paths

To satisfy Objectives **O1–O4**, the Data Platform splits incoming financial market data into three specialized paths immediately after Kafka ingestion. No single database is forced to serve conflicting workloads.

See also:
- [Diagram 04: Overall Data Platform Architecture](../diagrams/data-platform/04-overall-data-platform.md)
- [Diagram 05: Data Ingestion Architecture](../diagrams/data-platform/05-data-ingestion.md)
- [Diagram 06: Event Streaming Architecture](../diagrams/data-platform/06-event-streaming.md)
- [Diagram 07: Bronze–Silver–Gold Medallion Data Flow](../diagrams/data-platform/07-bronze-silver-gold-flow.md)

---

## 2. Deep Dive: The Three Data Paths

### 2.1. Path A — Hot Data Path (`Binance WS -> Collector -> Kafka -> Hot Consumer -> Redis`)

| Design Dimension | Architectural Specification |
|---|---|
| **Responsibility** | Sub-15ms serving of latest prices, 24h rolling ticker snapshots, top-20 order book depth, and live WebSocket fan-out. |
| **Event Partitioning Strategy** | Kafka topics partitioned by `{provider}:{symbol}` (6 partitions initially). Guarantees all updates for a given trading pair arrive in strict partition order. |
| **Event Key Selection** | Kafka record key: `binance:BTCUSDT` (UTF-8 bytes). Redis keys: `market:v1:price:binance:BTCUSDT`, `market:v1:snapshot:binance:BTCUSDT`, `market:v1:orderbook:binance:BTCUSDT`. |
| **Latest-Value Update & Out-of-Order Strategy** | `consumer-hot-redis` executes an atomic Redis Lua script comparing incoming `exchange_event_time_ms` (or `last_update_id` for order books) against the stored field `exchange_event_time_ms`. If `incoming < stored`, the update is discarded and `hot_out_of_order_dropped_total` is incremented. |
| **Data Freshness Policy** | Data is considered **Fresh** when `(now_utc_ms - exchange_event_time_ms) <= 15,000 ms` (15s). Between `15s` and `300s`, responses return `meta.is_stale = true`. |
| **Cache Expiration & Invalidation** | Every hot key carries a sliding TTL (`300s` for price/snapshot, `120s` for order book). If a symbol is halted or disabled in `monitored_instruments`, an explicit `DEL` invalidation event clears its hot keys. |
| **Consumer Recovery** | On restart, `consumer-hot-redis` resumes from its last committed Kafka offset (or seeks to end minus 5 minutes if offset expired) and rapidly repopulates current state. During cold start, FastAPI transparently falls back to ClickHouse. |

---

### 2.2. Path B — Analytics Data Path (`Kafka -> ClickHouse Consumer -> ClickHouse -> Materialized Views`)

| Design Dimension | Architectural Specification |
|---|---|
| **Responsibility** | High-speed historical candle/trade range queries, real-time OHLCV rollups, statistical aggregations, BI dashboards (Superset), and Agent quantitative tool queries. |
| **Table Engine & Deduplication** | Base tables use `ReplacingMergeTree(ingested_at)` (for trades/orderbooks) and `ReplacingMergeTree(exchange_event_time)` (for klines/tickers) to handle at-least-once duplicate Kafka deliveries deterministically. |
| **Primary Ordering & Sorting Key** | Low-cardinality filter columns first, followed by monotonic timestamp: e.g., `ORDER BY (provider, symbol, interval, open_time)` for `market_klines`; `ORDER BY (provider, symbol, trade_time, trade_id)` for `market_trades`. |
| **Partitioning Strategy** | Monthly partitioning `PARTITION BY toYYYYMM(open_time)` (or `toYYYYMM(trade_time)`). Prevents partition explosion while enabling fast partition pruning and TTL drops. |
| **Batch Insertion Strategy** | Never insert row-by-row. `consumer-analytics-ch` buffers records in memory and flushes every `1.0 second` or `5,000 rows` per table using ClickHouse native columnar batch inserts before committing Kafka offsets. |
| **Materialized View Strategy** | Incremental `AggregatingMergeTree` Materialized Views compute `1h` and `1d` rollups and hourly symbol statistics (`mv_symbol_stats_hourly`) on insert without full-table scans. |
| **Data Retention Policy** | Raw `market_trades` and `order_book_snapshots` retain 90 days in ClickHouse (`TTL toDateTime(trade_time) + INTERVAL 90 DAY DELETE`); `market_klines` (`1m`, `5m`, `1h`, `1d`) retain 5+ years in ClickHouse. Full raw history is preserved permanently in MinIO/Iceberg. |

---

### 2.3. Path C — Historical Data Lake Path (`Kafka / REST -> MinIO -> Parquet -> Iceberg -> PySpark -> dbt`)

| Medallion Layer | Storage Location & Format | Owning Engine | Transformation & Quality Responsibility |
|---|---|---|---|
| **Bronze (Raw)** | `s3://market-data/bronze/{event_type}/` (Parquet + Iceberg `lakehouse.bronze.*`) | `consumer-lakehouse-bronze` & `collector-rest` | Immutable append-only archive of raw `EventEnvelopeV1` records partitioned by `(provider, ingestion_date)`. Preserves exact source payload and lineage metadata (`event_id`, `ingested_at`). |
| **Silver (Cleaned & Standardized)** | `s3://market-data/silver/{entity}/` (Apache Iceberg `lakehouse.silver.*`) | **Apache Spark (PySpark)** orchestrated by Airflow | Reads incremental Bronze snapshots, enforces exact `Decimal(38,18)` types and UTC timestamps, deduplicates by natural keys via Iceberg `MERGE INTO`, and validates invariants via **Great Expectations**. |
| **Gold (Curated Business & Analytics)** | `s3://market-data/gold/{mart}/` & ClickHouse `analytics.mart_*` | **dbt Core** orchestrated by Airflow | Executes modular SQL models producing daily market summaries, realized volatility term structures, liquidity/spread profiles, and cross-asset return matrices. |

#### Strict Non-Duplication Rule Across Processing Engines
1. **Python Collectors**: Only translate provider JSON $\rightarrow$ canonical `EventEnvelopeV1`. No business aggregations.
2. **PySpark**: Only performs Bronze $\rightarrow$ Silver dataset standardization, deduplication, historical backfill merges, and Iceberg compaction.
3. **dbt Core**: Owns all Silver $\rightarrow$ Gold SQL business logic and analytical mart definitions.

---

## 3. Complete 12-Stage Data Lifecycle Specification

Every stage of the platform's data lifecycle has a strictly defined contract, technology owner, and failure recovery path:

| Stage | Responsibility | Input | Output | Data Contract | Technology | Failure Handling | Dependencies |
|---|---|---|---|---|---|---|---|
| **1. Data Source Discovery** | Fetch exchange metadata (`exchangeInfo`), trading status, tick size, and reconcile against configured `monitored_instruments`. | Binance `GET /api/v3/exchangeInfo` + Operator config | Active symbol subscription list in PostgreSQL | `InstrumentMetadataV1` | `collector-rest` + PostgreSQL | Retries with backoff; retains last known valid symbol catalog if exchange endpoint fails. | PostgreSQL, Binance REST |
| **2. Data Ingestion** | Maintain live WebSocket streams and execute paginated REST historical/gap-fill fetches; normalize to canonical decimals and UTC. | Raw Binance WS frames & REST JSON | Normalized in-memory `EventEnvelopeV1` objects | `EventEnvelopeV1` | `collector-ws`, `collector-rest` | Auto-reconnects WS with jitter; records disconnection gap in `ingestion_watermarks` for automatic REST backfill. | Stage 1, Binance APIs |
| **3. Event Validation** | Enforce strict schema, type, enum, and non-negative price/quantity invariants; generate deterministic UUIDv5 `event_id`. | Normalized candidate dictionary | Validated `EventEnvelopeV1` or `DeadLetterEnvelopeV1` | Pydantic v2 Strict Schemas | `src/shared/contracts/` in Collectors | Malformed events never crash the collector; they are wrapped with stack trace and published to `market.dlq.v1`. | Stage 2 |
| **4. Event Distribution** | Durably append validated events to partitioned topic logs and fan out to independent consumer groups. | Validated `EventEnvelopeV1` | Partitioned Kafka log records (`{provider}:{symbol}`) | Kafka Topic Contracts (`market.raw.*.v1`) | Apache Kafka (KRaft) | Producer `acks=all`, `enable.idempotence=true`, local buffer queue; consumer group pause/resume on downstream backpressure. | Stage 3, Kafka |
| **5. Raw Data Persistence (Bronze)** | Flush buffered raw event streams and REST backfill batches into immutable columnar files in the Data Lake. | Kafka raw topics / REST chunks | ZSTD Parquet files registered in Iceberg Bronze | `lakehouse.bronze.*` schema | `consumer-lakehouse-bronze`, MinIO, Parquet, Iceberg | Commits Kafka offsets only after S3 `PutObject` + Iceberg append succeeds; idempotent file naming by `(topic, partition, start_offset, end_offset)`. | Stage 4, MinIO |
| **6. Data Processing (Silver & Real-Time Sinks)** | Project hot state into Redis, micro-batch insert into ClickHouse base tables, and run batch Bronze $\rightarrow$ Silver deduplication in Iceberg. | Kafka raw topics & Bronze Iceberg tables | Redis Hashes, ClickHouse `ReplacingMergeTree` rows, Silver Iceberg tables | Silver Iceberg & ClickHouse base DDL | `consumer-hot-redis`, `consumer-analytics-ch`, PySpark | Redis uses Lua monotonic guard; ClickHouse consumer retries batch before offset commit; PySpark uses ACID Iceberg `MERGE INTO`. | Stage 4, Stage 5 |
| **7. Data Modeling (Gold & Analytical Views)** | Transform cleaned Silver and ClickHouse base tables into business-ready analytical marts and rollups. | Silver Iceberg & ClickHouse base tables | Gold Iceberg tables, ClickHouse `mart_*` tables & Materialized Views | dbt `schema.yml` contracts | dbt Core + ClickHouse Materialized Views | Incremental dbt runs with transactional table swap / partition overwrite; Airflow alerts and halts downstream DAG tasks on SQL failure. | Stage 6, Airflow |
| **8. Data Quality Validation** | Verify completeness, freshness, uniqueness, and financial invariants (`high >= low`, `high >= open`, `volume >= 0`, no timestamp gaps). | ClickHouse tables & Silver/Gold Iceberg tables | Validation results JSON + Prometheus metrics + Quarantine flags | Great Expectations Expectation Suites | Great Expectations orchestrated by Airflow | Failed critical expectations block Gold promotion, emit alerts to `market.anomalies.v1` / Grafana, and preserve prior snapshot via Iceberg time-travel. | Stage 6, Stage 7 |
| **9. Data Storage Optimization** | Compact small Parquet files, expire old Iceberg snapshots, merge ClickHouse parts, and enforce TTL retention policies. | Fragmented Iceberg files & ClickHouse parts | Compacted Parquet files ($128-256\text{ MB}$), pruned TTL partitions | Iceberg Maintenance & ClickHouse TTL policies | Airflow + PySpark Iceberg Actions + ClickHouse TTL | Non-destructive metadata-locked compactions; runs during off-peak schedules with bounded CPU/IO quotas. | Stage 5, Stage 6, Stage 7 |
| **10. Data Serving** | Expose low-latency hot state, bounded historical/analytical queries, BI dashboards, and read-only deterministic Agent tools. | Redis, ClickHouse, PostgreSQL | REST JSON, WebSocket frames, SSE streams, Superset charts, Tool outputs | OpenAPI v1 (`api-specification.md`) & Tool Schemas | FastAPI, Redis, ClickHouse, Apache Superset, Tool Gateway | Redis miss/outage falls back to ClickHouse; unbounded queries rejected with `HTTP 422`; circuit breakers protect databases. | Stage 6, Stage 7, Stage 8 |
| **11. Data Monitoring** | Continuously measure ingestion throughput, consumer lag, end-to-end data freshness, API latency percentiles, and error rates. | `/metrics` endpoints, Kafka offsets, table max timestamps | Time-series metrics, Grafana dashboards, anomaly triggers | Prometheus Metric Exposition Format | Prometheus + Grafana + `StatisticalAnomalyDetector` | Scraping failures trigger immediate `TargetDown` alerts; staleness breaches emit `MarketAnomalyEventV1`. | All Stages |
| **12. Data Governance** | Enforce RBAC, credential isolation, audit logging, schema evolution rules, and end-to-end data lineage tracking. | User/Agent requests, schema changes, tool executions | Immutable audit rows (`agent_tool_invocations`, `audit_logs`), dbt lineage graph | Governance & Security Policies (`10-security-and-governance.md`) | PostgreSQL, FastAPI Auth, dbt Docs, Controlled Tool Gateway | Unauthorized requests rejected (`HTTP 401/403`); every Agent report retains cryptographic/structural provenance to source tables and time windows. | All Stages |

