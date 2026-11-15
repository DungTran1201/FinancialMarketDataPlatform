# Diagram 04: Overall Data Platform Architecture (`DIAG-DATA-004`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-DATA-004` |
| **Title** | Overall Data Platform Architecture |
| **Diagram Category** | `docs/diagrams/data-platform/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart LR)` |
| **Status** | `IMPLEMENTED` / `PARTIALLY_IMPLEMENTED` (v0.1 Python Lakehouse & DQ engines active; PySpark/dbt-runner/Airflow/GE Phase 2 targets `[PLANNED]`) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/04-data-platform-architecture.md` |
| **Canonical Model Reference** | `models/data-platform/datasets.yaml` |
| **Related Artifact IDs** | `FR-01`..`FR-10`, `COMP-001`..`COMP-014` |

## Architectural Explanation

The **Overall Data Platform Architecture** illustrates the **Streaming-First Hybrid Lakehouse** divided into three parallel workload-optimized data paths (`AC-004` non-summed branches):
1. **Hot Data Path (Sub-Second Latency — `[IMPLEMENTED]`)**: `Collector -> Kafka -> HotStateProjector -> Redis` for latest prices, 24h ticker snapshots, and live observability fan-out (`SSE /api/v1/observability/stream` & `WS /ws/v1/observability/stream`; `/ws/v1/market/stream` is `[PLANNED]`).
2. **Analytics Data Path (Micro-Batch OLAP — `[IMPLEMENTED]`)**: `Kafka -> ClickHouseBatchSink -> ClickHouse ReplacingMergeTree -> Materialized Views` for historical candle queries, trade history, rolling market statistics, and Apache Superset BI dashboards.
3. **Historical Data Lakehouse Path (Medallion — v0.1 `[IMPLEMENTED]` + Phase 2 `[PLANNED]`)**: v0.1 Python engines (`BronzeParquetArchiver`, `SilverLakehouseMergeEngine`, `GoldMartEngine`, `DataQualityGateEngine` with `DQ-KLINE-001..005` & `DQ-TRADE-001..003`) write `.local_lakehouse/` Parquet + Iceberg v2 manifests and MinIO S3; full distributed `PySpark`, `dbt Core` container, `Apache Airflow`, and `Great Expectations` suites remain `[PLANNED — Phase 2]`.

```mermaid
flowchart LR
    subgraph Sources["1. Data Sources"]
        WS["Binance WebSocket API"]
        REST["Binance REST API"]
    end

    subgraph Ingestion["2. Ingestion & Normalization"]
        WSCol["WebSocket Collector<br/>(Stub CLI PROP-APP-002 / Pipeline)"]
        RESTCol["REST Historical Collector<br/>(HTTP Client + Backfill Worker)"]
        DLQ[("Kafka DLQ<br/>market.dlq.v1")]
    end

    subgraph Streaming["3. Event Backbone (1-Node KRaft)"]
        Kafka[("Apache Kafka<br/>trades | klines | tickers | orderbook")]
    end

    subgraph HotPath["4A. Hot Data Path (<500ms)"]
        HotCons["HotStateProjector"]
        Redis[("Redis 7<br/>Latest Price, Snapshot, Top-20 Book")]
    end

    subgraph AnalyticsPath["4B. Analytics Data Path (1-5s)"]
        CHCons["ClickHouseBatchSink"]
        CHBase[("ClickHouse Base Tables<br/>ReplacingMergeTree")]
        CHMV[("ClickHouse Materialized Views<br/>AggregatingMergeTree")]
    end

    subgraph LakehousePath["4C. Historical Lakehouse Path (Medallion)"]
        BronzeWriter["BronzeParquetArchiver (v0.1)"]
        Bronze[("MinIO / .local_lakehouse BRONZE<br/>Immutable Raw Parquet")]
        Spark["SilverLakehouseMergeEngine (v0.1)<br/>+ PySpark [PLANNED Phase 2]"]
        Silver[("SILVER Iceberg v2<br/>Clean Canonical Tables")]
        DBT["GoldMartEngine (v0.1)<br/>+ dbt Core [PLANNED Phase 2]"]
        Gold[("GOLD Analytical Marts<br/>& ClickHouse Projections")]
    end

    subgraph Governance["5. Orchestration & Quality"]
        Airflow["Apache Airflow [PLANNED Phase 2]"]
        GE["DataQualityGateEngine (v0.1 Active)<br/>+ Great Expectations [PLANNED]"]
    end

    subgraph Serving["6. Data Serving"]
        FastAPI["FastAPI Backend<br/>(REST / SSE / Obs WS; Market WS PLANNED)"]
        Superset["Apache Superset<br/>(BI Dashboards)"]
        ToolGW["Agent Tool Gateway<br/>(10 Read-Only Tools)"]
    end

    WS --> WSCol
    REST --> RESTCol
    WSCol --> Kafka
    RESTCol --> Kafka
    WSCol -.->|"Invalid Payload"| DLQ

    Kafka --> HotCons --> Redis
    Kafka --> CHCons --> CHBase --> CHMV
    Kafka --> BronzeWriter --> Bronze
    RESTCol -->|"Bulk Backfill Parquet"| Bronze

    Bronze --> Spark --> Silver --> GE --> DBT --> Gold
    Silver -.->|"Historical Recovery / Backfill"| CHBase

    Airflow -.->|"Orchestrates [PLANNED]"| RESTCol & Spark & DBT & GE

    Redis --> FastAPI
    CHBase --> FastAPI
    CHMV --> FastAPI
    CHMV --> Superset
    Gold --> Superset
    Redis --> ToolGW
    CHBase --> ToolGW
    CHMV --> ToolGW
```

