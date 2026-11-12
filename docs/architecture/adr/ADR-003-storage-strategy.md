# ADR-003: Polyglot Storage Strategy & Workload Separation

- **Status**: Accepted
- **Date**: 2026-11-12
- **Deciders**: Data Platform & Backend Architecture Team

---

## 1. Decision Title

Adopt a **Workload-Segregated Polyglot Storage Architecture** comprising **Redis** (Hot Ephemeral State), **ClickHouse** (Real-time & Historical OLAP), **MinIO + Apache Parquet + Apache Iceberg** (Medallion Lakehouse System of Record for Raw/Historical Data), and **PostgreSQL** (Transactional Control Plane & Agent State).

---

## 2. Context

The platform serves four fundamentally incompatible data access patterns:
1. **Hot Key-Value Access**: Sub-15ms lookups for latest symbol prices, best bid/ask, and real-time market snapshots at high request concurrency.
2. **High-Speed Time-Series OLAP**: Range scans, OHLCV rollups, volatility/correlation calculations, and BI dashboard queries over millions of trades and candles.
3. **Immutable Historical Archive & Batch Reprocessing**: Cost-effective retention of raw events, schema-evolvable tables, and large-scale historical backfills.
4. **ACID Transactional State**: User accounts, RBAC permissions, API keys, monitored symbol configurations, backfill watermarks, and LangGraph agent execution states.

---

## 3. Problem Statement

No single database engine can optimally satisfy sub-15ms key-value state lookups, high-compression columnar time-series analytics, ACID relational control metadata, and petabyte-scalable raw file archival. How do we assign strict data ownership across the approved storage engines without creating ambiguity or dual-source-of-truth conflicts?

---

## 4. Selected Option

Enforce strict workload and system-of-record boundaries across the four storage engines:

| Storage Engine | Primary Role | System of Record For | Explicitly Prohibited Usage |
|---|---|---|---|
| **PostgreSQL** | Transactional OLTP Database | Users, RBAC, API keys, platform config, ingestion watermarks, job states, Agent runs & tool audit logs. | Storing high-frequency market ticks, klines, or order book snapshots. |
| **Redis** | Hot Data Cache & Pub/Sub Fanout | **None** (Ephemeral derived projection only). Holds latest price, 24h snapshot, top-20 order book, rate-limit counters, and short-TTL query cache. | Acting as a durable system of record or storing historical time-series arrays. |
| **ClickHouse** | Real-Time & Historical OLAP Database | Serving analytical time-series queries (`market_trades`, `market_klines`, `market_tickers`, `order_book_snapshots`) and Materialized Views for API and Superset BI. | Storing user credentials, RBAC transactions, or executing frequent single-row `UPDATE`/`DELETE` mutations. |
| **MinIO + Parquet + Iceberg** | Lakehouse Storage (Bronze / Silver / Gold) | Durable, immutable raw event archive (**Bronze**) and canonical deduplicated historical datasets (**Silver** / **Gold**). | Serving synchronous low-latency REST API requests directly. |

---

## 5. Alternative Options Considered

### Alternative A: PostgreSQL Alone for Both Control Plane and Market Time-Series
- **Rejection Reason**: Standard PostgreSQL B-Tree indexes and heap storage suffer severe write amplification and bloat under continuous multi-symbol tick ingestion and perform poorly on wide time-range columnar aggregations compared to ClickHouse.

### Alternative B: ClickHouse as the Single Database (Including Users, Auth, and Agent State)
- **Rejection Reason**: Violates Constraint 7 and Section 9.8. ClickHouse lacks row-level ACID transactions, foreign key integrity, and efficient point-row updates required for authentication, RBAC, job state machines, and LangGraph checkpointing.

### Alternative C: Querying Iceberg/Parquet on MinIO Directly from FastAPI
- **Rejection Reason**: Violates Section 9.4. S3/MinIO object listings and Parquet footer reads introduce hundreds of milliseconds to seconds of latency per query and cannot support high-concurrency API traffic.

---

## 6. Decision Rationale

- **ClickHouse (`ReplacingMergeTree` & `AggregatingMergeTree`)** achieves $10\times - 100\times$ higher compression and scan speed for financial time-series than row-oriented stores while tolerating at-least-once Kafka ingestion via deterministic sort keys `(provider, symbol, interval, open_time)`.
- **MinIO + Iceberg** provides ACID table snapshots, hidden partitioning, time-travel, and schema evolution over Parquet files, acting as the ultimate recovery reservoir that can rebuild ClickHouse tables at any time.
- **Redis** absorbs $80\%+$ of high-frequency price/snapshot polling traffic in memory, shielding ClickHouse from repetitive point lookups.
- **PostgreSQL** guarantees strict ACID consistency for security, configuration, and workflow state transitions.

---

## 7. Benefits

- **Predictable Query Performance**: Each query category routes to an engine specifically architected for its access pattern.
- **Rebuildability**: Both Redis (hot projection) and ClickHouse (OLAP projection) can be reconstructed from Kafka (short term) or Iceberg Silver/Bronze tables (long term).
- **Clear Operational Ownership**: Schema migrations for PostgreSQL (Alembic), ClickHouse (SQL DDL migrations), and Iceberg/dbt are cleanly separated.

---

## 8. Drawbacks

- Requires maintaining schema parity between canonical Kafka events, ClickHouse DDL, and Iceberg table definitions.
- Requires explicit fallback logic in the Backend when Redis is cold or unavailable.

---

## 9. Architectural Limitations

- **ClickHouse Deduplication Is Eventual**: `ReplacingMergeTree` deduplicates asynchronously during background merges. Queries requiring strict immediate deduplication must use `FINAL` (restricted to bounded single-symbol/short-window queries) or `argMax(..., exchange_event_time)` group-by patterns.
- **Lakehouse Small-File Problem**: Writing Parquet files too frequently creates metadata overhead; Bronze writers must batch by time/size ($5-15\text{ minutes}$ or $\ge 64\text{ MB}$) and run scheduled Iceberg compaction.

---

## 10. Operational Implications

- **ClickHouse Partitioning & Retention**: Partition large tables by `toYYYYMM(trade_time)` or `toYYYYMM(open_time)`. Apply TTL policies to raw high-volume ticks (e.g., 90 days in ClickHouse) while retaining complete history in MinIO/Iceberg.
- **PostgreSQL Connection Pooling**: Use async connection pooling (`asyncpg` / SQLAlchemy `AsyncEngine`) with bounded pool sizes (`pool_size=10, max_overflow=10`) to prevent connection exhaustion.

---

## 11. Consequences

- Every repository interface in the Backend Application Layer explicitly targets its designated store (`MarketHotStorePort` $\rightarrow$ Redis with ClickHouse fallback; `MarketAnalyticsRepositoryPort` $\rightarrow$ ClickHouse; `ControlPlaneRepositoryPort` $\rightarrow$ PostgreSQL).

---

## 12. Conditions That Could Invalidate This Decision

1. If historical raw data volume grows beyond single-cluster MinIO capacity, object storage can be switched to cloud S3/GCS via configuration (`S3_ENDPOINT_URL`) without changing Parquet/Iceberg code.
2. If real-time sub-millisecond point updates with strict transactional semantics on analytical tables are required, ClickHouse's eventual merge model would be unsuitable.

