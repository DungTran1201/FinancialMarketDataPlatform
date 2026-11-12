# Diagram 06: Event Streaming Architecture

## Architectural Explanation

The **Event Streaming Architecture** illustrates how Apache Kafka decouples event producers from four independent consumer groups, guaranteeing:
1. **Partition-Level Ordering**: Every topic uses `{provider}:{symbol}` (or `{provider}:{symbol}:{interval}` for klines) as the partition key, ensuring all events for `binance:BTCUSDT` land in the exact same partition in arrival order.
2. **Independent Consumer Group Isolation**:
   - `cg.hot.redis.v1`: Low-latency single-event/pipelined updates to Redis with Lua monotonic timestamp guards.
   - `cg.analytics.clickhouse.v1`: Micro-batched ($1\text{ s}$ or $5,000$ events) bulk inserts into ClickHouse `ReplacingMergeTree` tables; manual offset commit occurs only after ClickHouse write confirmation.
   - `cg.lakehouse.bronze.v1`: Buffered Parquet file flushes ($5\text{ m}$ or $64\text{ MB}$) to MinIO Bronze storage.
   - `cg.anomaly.detector.v1`: Evaluates closed klines and ticker shifts against deterministic statistical thresholds and emits deduplicated alerts to `market.anomalies.v1`.

```mermaid
flowchart LR
    subgraph Producers["Producers"]
        WSCol["collector-ws"]
        RESTCol["collector-rest"]
    end

    subgraph KafkaBroker["Apache Kafka (Partitioned by provider:symbol)"]
        direction TB
        subgraph TopicTrades["market.raw.trades.v1 (6 Partitions)"]
            P0["Partition 0 (e.g. binance:BTCUSDT)"]
            P1["Partition 1 (e.g. binance:ETHUSDT)"]
            PN["Partition 2..5 (Other Symbols)"]
        end
        TopicKlines["market.raw.klines.v1 (6 Partitions)"]
        TopicTickers["market.raw.tickers.v1 (6 Partitions, Compact+Delete)"]
        TopicBook["market.raw.orderbook.v1 (6 Partitions)"]
        TopicAnomaly["market.anomalies.v1 (3 Partitions)"]
        TopicDLQ["market.dlq.v1 (3 Partitions)"]
    end

    subgraph ConsumerGroups["Independent Kafka Consumer Groups"]
        CGHot["Consumer Group: cg.hot.redis.v1<br/>(Low-Latency Pipelined Upsert)"]
        CGCH["Consumer Group: cg.analytics.clickhouse.v1<br/>(1s / 5000-Row Micro-Batch Buffer)"]
        CGBronze["Consumer Group: cg.lakehouse.bronze.v1<br/>(5m / 64MB Parquet Buffer)"]
        CGAnomaly["Consumer Group: cg.anomaly.detector.v1<br/>(Statistical Z-Score & Freshness Check)"]
        CGAgent["Consumer Group: cg.agent.anomaly.v1<br/>(Cooldown-Gated Investigation Worker)"]
    end

    subgraph Sinks["Downstream Sinks"]
        Redis[("Redis 7 Hot Store")]
        ClickHouse[("ClickHouse OLAP")]
        MinIO[("MinIO Bronze Lakehouse")]
        AgentWorker["LangGraph Agent Worker"]
    end

    WSCol --> TopicTrades & TopicKlines & TopicTickers & TopicBook
    RESTCol --> TopicTrades & TopicKlines
    WSCol -.->|"Malformed"| TopicDLQ

    TopicTrades & TopicKlines & TopicTickers & TopicBook --> CGHot
    TopicTrades & TopicKlines & TopicTickers & TopicBook --> CGCH
    TopicTrades & TopicKlines & TopicBook --> CGBronze
    TopicKlines & TopicTickers --> CGAnomaly

    CGHot -->|"Atomic Lua (if event_ts >= stored_ts)"| Redis
    CGCH -->|"Async Bulk Insert + Commit Offset"| ClickHouse
    CGBronze -->|"Write ZSTD Parquet + Commit Offset"| MinIO
    CGAnomaly -->|"Breach Detected"| TopicAnomaly
    TopicAnomaly --> CGAgent --> AgentWorker
```

