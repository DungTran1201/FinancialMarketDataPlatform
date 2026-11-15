# Diagram 08 — End-to-End Data Platform v0.1 12-Stage Pipeline (`DIAG-DATA-008`)

## 1. Purpose

Illustrates the complete, zero-mock **12-Stage Data Platform v0.1** execution pipeline (`DataPlatformV01Pipeline` in `src/lakehouse/orchestration/pipeline.py`), tracing data from Stage 1 (`exchangeInfo` Discovery) through Stage 12 (Governance Lineage & Prometheus SLIs).

---

## 2. Mermaid Flowchart (`DIAG-DATA-008`)

```mermaid
flowchart TD
    subgraph S1_S3["Stages 1-3: Discovery, Ingestion & Validation"]
        EX["Binance Spot HTTP / WS Protocol<br/>(/api/v3/exchangeInfo & /api/v3/klines)"]
        DISC["Stage 1: ExchangeDiscovery<br/>(tick_size, lot_size, min_notional)"]
        WS["Stage 2a: WebSocketStreamCollector<br/>(SequenceAndGapDetector + Jitter Backoff)"]
        REST["Stage 2b: HistoricalRestBackfillWorker<br/>(TokenBucketRateLimiter + Watermark DB)"]
        NORM["Stage 3: BinancePayloadNormalizer<br/>(UUIDv5 event_id + Decimal Invariants)"]
        DLQ["Kafka DLQ Topic<br/>(market.dlq.v1)"]
    end

    subgraph S4_S6["Stages 4-6: Partitioned Streaming, Hot/OLAP Sinks & Silver Lakehouse"]
        KAFKA["Stage 4: PartitionedEventStreamingBroker<br/>(6 Partitions by provider:symbol)"]
        REDIS["Stage 6a: HotStateProjector (Redis 7)<br/>(Monotonic Lua Guard BR-003)"]
        CH["Stage 6b: ClickHouseBatchSink<br/>(ReplacingMergeTree Micro-Batch)"]
        BRONZE["Stage 5: BronzeParquetArchiver<br/>(Immutable ZSTD Parquet by Date)"]
        SILVER["Stage 6c: SilverLakehouseMergeEngine<br/>(MERGE INTO silver.market_klines & trades)"]
    end

    subgraph S7_S9["Stages 7-9: Quality Gates, Gold Marts & Iceberg Compaction"]
        DQ["Stage 8: DataQualityGateEngine<br/>(DQ-KLINE-001..005 Pre-Promotion Gate)"]
        GOLD1["Stage 7a: gold.fct_daily_market_summary<br/>(Daily OHLCV, VWAP, Return %)"]
        GOLD2["Stage 7b: gold.fct_realized_volatility<br/>(Log-Return Volatility & Max Drawdown)"]
        GOLD3["Stage 7c: gold.fct_orderbook_liquidity<br/>(Spread bps, Top-20 Depth & Imbalance)"]
        COMP["Stage 9: Iceberg v2 Compaction<br/>(Small-File Merge + metadata.json)"]
    end

    subgraph S10_S12["Stages 10-12: Serving, Prometheus Observability & Lineage"]
        SERVE["Stage 10: Serving Layer<br/>(svc-market-hot, svc-analytics-quant, Tool Gateway)"]
        PROM["Stage 11: DataObservabilityMetricsCollector<br/>(Prometheus fmdp_* Counters & Gauges)"]
        LIN["Stage 12: DataLineageGovernanceRegistry<br/>(12 Datasets & Directed Lineage DAG)"]
    end

    EX --> DISC
    DISC --> WS
    DISC --> REST
    WS --> NORM
    REST --> NORM
    NORM -- "Invalid Payload" --> DLQ
    NORM -- "Valid EventEnvelopeV1" --> KAFKA
    KAFKA --> REDIS
    KAFKA --> CH
    KAFKA --> BRONZE
    BRONZE --> SILVER
    SILVER --> DQ
    DQ -- "PASSED (can_promote_to_gold=true)" --> GOLD1
    DQ -- "PASSED" --> GOLD2
    DQ -- "PASSED" --> GOLD3
    SILVER --> COMP
    REDIS --> SERVE
    CH --> SERVE
    GOLD1 --> SERVE
    GOLD2 --> SERVE
    GOLD3 --> SERVE
    KAFKA --> PROM
    DQ --> PROM
    GOLD1 --> LIN
    COMP --> LIN
```

---

## 3. Pipeline Execution Sequencing Note (Stage 8 Pre-Promotion Gate)

In the runtime orchestrator `DataPlatformV01Pipeline` (`src/lakehouse/orchestration/pipeline.py`), **Stage 8 (Automated Data Quality Gates)** is executed chronologically **before** **Stage 7 (Gold Layer Analytical Marts)**:
- **Silver Deduplication (Stage 6)** outputs standardized candidate datasets (`silver.market_klines` and `silver.market_trades`).
- **Quality Gate Engine (Stage 8)** evaluates rules `DQ-KLINE-001` through `DQ-KLINE-005` (monotonic timestamps, OHLC envelope $H \ge \max(O,C)$ and $L \le \min(O,C)$, non-negative volume, natural-key uniqueness).
- **Gold Mart Materialization (Stage 7)** proceeds **only if** `can_promote_to_gold=true`. If critical quality gates fail, promotion to Gold is blocked and unvalidated records are isolated.
- **Storage Compaction (Stage 9)** subsequently merges small Parquet files and generates Apache Iceberg v2 snapshot manifests (`metadata.json`).


