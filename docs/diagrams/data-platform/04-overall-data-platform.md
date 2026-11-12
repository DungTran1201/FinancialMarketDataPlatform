# Diagram 04: Overall Data Platform Architecture

## Architectural Explanation

The **Overall Data Platform Architecture** illustrates the **Streaming-First Hybrid Lakehouse** divided into three workload-optimized data paths:
1. **Hot Data Path (Sub-Second Latency)**: `Binance WebSocket -> Collector -> Kafka -> Hot Consumer -> Redis` for latest prices, 24h ticker snapshots, and live WebSocket fan-out.
2. **Analytics Data Path (1–5s Micro-Batch OLAP)**: `Kafka -> ClickHouse Consumer -> ClickHouse ReplacingMergeTree -> Materialized Views` for low-latency historical candle queries, trade history, rolling market statistics, and Apache Superset BI dashboards.
3. **Historical Data Lake Path (Durable Medallion Lakehouse)**: `Kafka / REST Backfill -> MinIO (Parquet + Apache Iceberg) -> PySpark (Bronze to Silver) -> dbt Core (Silver to Gold)` orchestrated by Apache Airflow and validated by Great Expectations.

```mermaid
flowchart LR
    subgraph Sources["1. Data Sources"]
        WS["Binance WebSocket API"]
        REST["Binance REST API"]
    end

    subgraph Ingestion["2. Ingestion & Normalization"]
        WSCol["WebSocket Collector"]
        RESTCol["REST Historical Collector"]
        DLQ[("Kafka DLQ<br/>market.dlq.v1")]
    end

    subgraph Streaming["3. Event Backbone"]
        Kafka[("Apache Kafka<br/>trades | klines | tickers | orderbook")]
    end

    subgraph HotPath["4A. Hot Data Path (<500ms)"]
        HotCons["Hot Cache Consumer"]
        Redis[("Redis 7<br/>Latest Price, Snapshot, Top-20 Book")]
    end

    subgraph AnalyticsPath["4B. Analytics Data Path (1-5s)"]
        CHCons["ClickHouse Micro-Batch Sink"]
        CHBase[("ClickHouse Base Tables<br/>ReplacingMergeTree")]
        CHMV[("ClickHouse Materialized Views<br/>AggregatingMergeTree")]
    end

    subgraph LakehousePath["4C. Historical Lakehouse Path (Medallion)"]
        BronzeWriter["Bronze Parquet Archiver"]
        Bronze[("MinIO / Iceberg: BRONZE<br/>Immutable Raw Events")]
        Spark["PySpark Batch Processing<br/>Deduplication & Standardization"]
        Silver[("MinIO / Iceberg: SILVER<br/>Clean Canonical Tables")]
        DBT["dbt Core Transformations<br/>Business & Factor Models"]
        Gold[("MinIO / Iceberg & CH: GOLD<br/>Curated Analytical Marts")]
    end

    subgraph Governance["5. Orchestration & Quality"]
        Airflow["Apache Airflow"]
        GE["Great Expectations"]
    end

    subgraph Serving["6. Data Serving"]
        FastAPI["FastAPI Backend<br/>(REST / WebSocket)"]
        Superset["Apache Superset<br/>(BI Dashboards)"]
        ToolGW["Agent Tool Gateway<br/>(Read-Only Deterministic)"]
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

    Bronze --> Spark --> Silver --> DBT --> Gold
    Silver -->|"Historical Recovery / Backfill"| CHBase

    Airflow -.->|"Orchestrates"| RESTCol
    Airflow -.->|"Orchestrates"| Spark
    Airflow -.->|"Orchestrates"| DBT
    Airflow -.->|"Triggers"| GE
    GE -.->|"Validates"| Silver
    GE -.->|"Validates"| CHBase

    Redis --> FastAPI
    CHBase --> FastAPI
    CHMV --> FastAPI
    CHMV --> Superset
    Gold --> Superset
    Redis --> ToolGW
    CHBase --> ToolGW
    CHMV --> ToolGW
```

