# Diagram 10: Selective CQRS Read/Write Architecture

## Architectural Explanation

The **CQRS Read/Write Architecture Diagram** illustrates how **Selective CQRS** is applied strictly where write and read workloads diverge:
- **High-Volume Market & Analytical Domains (CQRS Enabled)**:
  - **Write Side (Ingestion & Projection Pipeline)**: External exchange streams and REST backfills flow through Collectors $\rightarrow$ Kafka $\rightarrow$ specialized projectors (`consumer-hot-redis`, `consumer-analytics-ch`, `consumer-lakehouse-bronze`).
  - **Read Side (Query Models)**: FastAPI Query Handlers read exclusively from read-optimized projections:
    - Redis Hashes/JSON for sub-15ms latest price, snapshot, and order book reads.
    - ClickHouse `ReplacingMergeTree` tables for historical candles and trades.
    - ClickHouse `AggregatingMergeTree` Materialized Views for pre-aggregated statistics and Superset dashboards.
- **Control & Transactional Domains (Standard CRUD — No CQRS)**:
  - Users, RBAC, Platform Configuration, and Agent Run Metadata use standard transactional PostgreSQL repositories for both commands and queries, avoiding unnecessary projection synchronization complexity.

```mermaid
flowchart TB
    subgraph WriteSide["CQRS Write Path (High-Throughput Ingestion & Projection)"]
        Binance["Binance WS & REST"]
        Collectors["Data Collectors<br/>(Validate & Normalize)"]
        Kafka[("Apache Kafka<br/>Partitioned Event Log")]
        ProjRedis["Hot State Projector<br/>(consumer-hot-redis)"]
        ProjCH["OLAP Micro-Batch Projector<br/>(consumer-analytics-ch)"]
        ProjLake["Lakehouse Archiver & Spark<br/>(Bronze -> Silver -> Gold)"]

        Binance --> Collectors --> Kafka
        Kafka --> ProjRedis
        Kafka --> ProjCH
        Kafka --> ProjLake
    end

    subgraph ReadModels["Read-Optimized Storage Projections"]
        RedisRM[("Redis Hot Read Model<br/>Latest Price, 24h Snapshot, Top-20 Depth")]
        CHBaseRM[("ClickHouse Historical Tables<br/>market_klines, market_trades")]
        CHMVRM[("ClickHouse Materialized Views<br/>mv_klines_1h/1d, mv_symbol_stats")]
        IcebergRM[("MinIO / Iceberg Silver & Gold<br/>Bulk Replay & Historical Recovery")]
    end

    subgraph ReadSide["CQRS Read Path (FastAPI Query Handlers & BI)"]
        HotQH["MarketQueryHandler<br/>(GET /market/prices, /snapshots)"]
        HistQH["HistoricalQueryHandler<br/>(GET /historical/klines, /trades)"]
        AnalyticsQH["AnalyticsQueryHandler<br/>(GET /analytics/statistics, /correlations)"]
        SupersetBI["Apache Superset & Agent Tool Gateway"]
    end

    subgraph TransactionalCRUD["Non-CQRS Transactional Domains (Standard Command/Query)"]
        ControlApp["IAM, Platform Config, Catalog & Agent State Handlers"]
        PostgresDB[("PostgreSQL 16<br/>Single ACID Source of Truth")]
        ControlApp <-->|"ACID Read & Write"| PostgresDB
    end

    ProjRedis -->|"Lua Monotonic Upsert"| RedisRM
    ProjCH -->|"Bulk Columnar Insert"| CHBaseRM
    CHBaseRM -->|"Incremental Trigger"| CHMVRM
    ProjLake -->|"Parquet + Iceberg Commit"| IcebergRM
    IcebergRM -.->|"Rebuild / Backfill Projection"| CHBaseRM

    RedisRM -->|"P95 < 15ms"| HotQH
    CHBaseRM -.->|"Fallback on Redis Miss/Failure"| HotQH
    CHBaseRM -->|"P95 < 80ms"| HistQH
    CHMVRM -->|"P95 < 75ms"| AnalyticsQH
    CHMVRM --> SupersetBI
    CHBaseRM --> SupersetBI
```

