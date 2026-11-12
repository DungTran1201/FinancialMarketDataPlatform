# Diagram 07: Bronze–Silver–Gold Medallion Data Flow

## Architectural Explanation

The **Bronze–Silver–Gold Data Flow** defines the exact division of responsibilities across the Lakehouse and OLAP layers so transformation logic is **never duplicated** across Python scripts, PySpark, and dbt Core:

1. **Bronze Layer (Raw Immutable Archive — Owned by `consumer-lakehouse-bronze` & `collector-rest`)**:
   - Format: ZSTD-compressed Apache Parquet registered in Apache Iceberg catalog (`lakehouse.bronze.*`) on MinIO.
   - Responsibility: Preserve exact incoming event envelopes (`event_id`, `ingested_at`, `raw_payload`, `exchange_event_time`) partitioned by `(provider, ingestion_date)`. Append-only; never mutated.
2. **Silver Layer (Cleaned, Deduplicated, Standardized — Owned by `PySpark` Batch Jobs)**:
   - Format: Apache Iceberg tables (`lakehouse.silver.trades`, `lakehouse.silver.klines`, `lakehouse.silver.order_book_snapshots`).
   - Responsibility: PySpark reads new Bronze snapshots, enforces strict `Decimal(38,18)` and UTC timestamp types, deduplicates records by natural key `(provider, symbol, trade_id)` or `(provider, symbol, interval, open_time)` using `MERGE INTO`, and runs **Great Expectations** validation suites before committing the Silver snapshot.
3. **Gold Layer (Business & Analytical Models — Owned by `dbt Core` & ClickHouse Materialized Views)**:
   - Format: Curated Iceberg tables (`lakehouse.gold.*`) and ClickHouse analytical marts (`analytics.mart_*`).
   - Responsibility: `dbt Core` executes version-controlled SQL models computing daily/hourly OHLCV rollups, realized volatility surfaces, liquidity/spread metrics, and cross-asset return tables consumed by Apache Superset, the Analytics API, and the Agent Tool Gateway.

```mermaid
flowchart LR
    subgraph RawSources["Ingestion Inputs"]
        KafkaStream["Kafka Raw Topics<br/>(trades, klines, orderbook)"]
        RESTBackfill["REST Historical Backfill<br/>(Paginated Batches)"]
    end

    subgraph BronzeLayer["BRONZE LAYER (MinIO + Iceberg Raw)"]
        BrzTrades[("bronze.raw_trades<br/>Append-Only Parquet")]
        BrzKlines[("bronze.raw_klines<br/>Append-Only Parquet")]
        BrzBook[("bronze.raw_orderbook<br/>Append-Only Parquet")]
    end

    subgraph SilverProcessing["PySpark + Great Expectations (Orchestrated by Airflow)"]
        SparkJob["PySpark Standardization & Deduplication<br/>(Type Casting, UTC Alignment, Iceberg MERGE INTO)"]
        GESilver["Great Expectations Suite<br/>(Null Checks, OHLC Invariants: High >= Low, Volume >= 0)"]
    end

    subgraph SilverLayer["SILVER LAYER (MinIO + Iceberg Clean)"]
        SlvTrades[("silver.market_trades<br/>Deduplicated by provider, symbol, trade_id")]
        SlvKlines[("silver.market_klines<br/>Deduplicated by provider, symbol, interval, open_time")]
        SlvBook[("silver.order_book_snapshots<br/>Validated Depth Arrays")]
    end

    subgraph GoldProcessing["dbt Core SQL Modeling"]
        DBTModels["dbt Core Incremental Models<br/>(Volatility, Returns, VWAP, Liquidity Factors)"]
        GEGold["Great Expectations & dbt Tests<br/>(Freshness, Referential & Statistical Bounds)"]
    end

    subgraph GoldLayer["GOLD LAYER (Iceberg + ClickHouse Analytical Marts)"]
        GldDaily[("gold.fct_daily_market_summary")]
        GldVol[("gold.fct_realized_volatility")]
        GldLiq[("gold.fct_orderbook_liquidity")]
    end

    KafkaStream --> BrzTrades & BrzKlines & BrzBook
    RESTBackfill --> BrzTrades & BrzKlines

    BrzTrades & BrzKlines & BrzBook --> SparkJob
    SparkJob --> GESilver
    GESilver -->|"Pass Validation"| SlvTrades & SlvKlines & SlvBook

    SlvTrades & SlvKlines & SlvBook --> DBTModels
    DBTModels --> GEGold
    GEGold -->|"Publish Marts"| GldDaily & GldVol & GldLiq
```

