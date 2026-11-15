# Diagram 10: Selective CQRS Read/Write Architecture (`DIAG-COMP-010`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-COMP-010` |
| **Title** | Selective CQRS Read/Write Architecture |
| **Diagram Category** | `docs/diagrams/backend/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart TB)` |
| **Status** | `IMPLEMENTED` (with `[TARGET SLO]` latency notes and `[PLANNED]` PySpark Phase 2 batch) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/05-backend-architecture.md` |
| **Canonical Model Reference** | `models/architecture/components.yaml`, `models/api/api.yaml` |
| **Related Artifact IDs** | `ADR-002`, `API-001`..`API-007`, `AC-002` |

## Architectural Explanation

The **CQRS Read/Write Architecture Diagram** illustrates how **Selective CQRS** is applied strictly where write and read workloads diverge:
- **High-Volume Market & Analytical Domains (CQRS Enabled)**:
  - **Write Side (Ingestion & Projection Pipeline)**: External exchange streams and REST backfills flow through Collectors $\rightarrow$ Kafka $\rightarrow$ specialized projectors (`HotStateProjector`, `ClickHouseBatchSink`, `BronzeParquetArchiver` + `SilverLakehouseMergeEngine` / `GoldMartEngine`).
  - **Read Side (Query Models)**: FastAPI Query Handlers read from read-optimized projections (`/api/v1/market/prices/{symbol}`, `/snapshots/{symbol}`, `/orderbook/{symbol}` from Redis with ClickHouse fallback; `/api/v1/historical/klines/{symbol}`, `/trades/{symbol}` and `/api/v1/analytics/statistics/{symbol}`, `/correlations`, `/anomalies` from ClickHouse / Analytical projections).
- **Control & Transactional Domains (Standard CRUD — No CQRS)**:
  - IAM, Platform Configuration, Watermarks, and Agent Run Metadata use SQLite WAL / PostgreSQL transactional persistence without CQRS projection overhead.

```mermaid
flowchart TB
    subgraph WriteSide["CQRS Write Path (High-Throughput Ingestion & Projection)"]
        Binance["Binance WS & REST"]
        Collectors["Data Collectors<br/>(Validate & Normalize)"]
        Kafka[("Apache Kafka KRaft<br/>Partitioned Event Log")]
        ProjRedis["Hot State Projector<br/>(HotStateProjector / cg.hot.redis.v1)"]
        ProjCH["OLAP Micro-Batch Projector<br/>(ClickHouseBatchSink / cg.analytics.clickhouse.v1)"]
        ProjLake["Lakehouse Archiver & Engines<br/>(Bronze->Silver->Gold v0.1; PySpark PLANNED)"]

        Binance --> Collectors --> Kafka
        Kafka --> ProjRedis
        Kafka --> ProjCH
        Kafka --> ProjLake
    end

    subgraph ReadModels["Read-Optimized Storage Projections"]
        RedisRM[("Redis Hot Read Model<br/>Latest Price, 24h Snapshot, Top-20 Depth")]
        CHBaseRM[("ClickHouse Historical Tables<br/>market_klines, market_trades")]
        CHMVRM[("ClickHouse Materialized Views<br/>mv_klines_1h/1d, mv_symbol_stats")]
        IcebergRM[("MinIO / .local_lakehouse Silver & Gold<br/>Bulk Replay & Historical Recovery")]
    end

    subgraph ReadSide["CQRS Read Path (FastAPI Query Handlers & BI)"]
        HotQH["MarketQueryHandler<br/>(GET /api/v1/market/prices/{symbol}, /snapshots/{symbol})"]
        HistQH["HistoricalQueryHandler<br/>(GET /api/v1/historical/klines/{symbol}, /trades/{symbol})"]
        AnalyticsQH["AnalyticsQueryHandler<br/>(GET /api/v1/analytics/statistics/{symbol}, /correlations, /anomalies)"]
        SupersetBI["Apache Superset & Agent Tool Gateway"]
    end

    subgraph TransactionalCRUD["Non-CQRS Transactional Domains (Standard Command/Query)"]
        ControlApp["IAM, Platform Config, Catalog & Agent State Handlers"]
        PostgresDB[("PostgreSQL 16 / SQLite WAL<br/>ACID Control State")]
        ControlApp <-->|"ACID Read & Write"| PostgresDB
    end

    ProjRedis -->|"Lua Monotonic Upsert"| RedisRM
    ProjCH -->|"Bulk Columnar Insert"| CHBaseRM
    CHBaseRM -->|"Incremental Trigger"| CHMVRM
    ProjLake -->|"Parquet + Iceberg v2 Commit"| IcebergRM
    IcebergRM -.->|"Rebuild / Backfill Projection"| CHBaseRM

    RedisRM -->|"TARGET P95 < 15ms"| HotQH
    CHBaseRM -.->|"Fallback on Redis Miss/Failure"| HotQH
    CHBaseRM -->|"TARGET P95 < 80ms"| HistQH
    CHMVRM -->|"TARGET P95 < 75ms"| AnalyticsQH
    CHMVRM --> SupersetBI
    CHBaseRM --> SupersetBI
```

