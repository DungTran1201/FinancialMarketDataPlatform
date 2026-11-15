# Diagram 06: Event Streaming Architecture (`DIAG-DATA-006`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-DATA-006` |
| **Title** | Event Streaming Architecture |
| **Diagram Category** | `docs/diagrams/data-platform/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart LR)` |
| **Status** | `IMPLEMENTED` / `PARTIALLY_IMPLEMENTED` (`cg.agent.anomaly.v1` standalone consumer `[PLANNED]`; Compose runs 1-node KRaft) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/08-data-flow-and-event-contracts.md`, `docs/specifications/data-contracts.md` |
| **Canonical Model Reference** | `models/data-platform/topics.yaml`, `models/data-platform/events.yaml` |
| **Related Artifact IDs** | `EVT-001`..`EVT-005`, `TOP-001`..`TOP-006`, `AC-004` |

## Architectural Explanation

The **Event Streaming Architecture** illustrates how Apache Kafka (configured as a **1-node KRaft** broker in `docker-compose.yml` alongside `PartitionedEventStreamingBroker` in runtime; 3-broker HA replication is a `[PLANNED]` production target) decouples producers from independent consumer groups (`AC-004` parallel post-Kafka branches):
1. **Partition-Level Ordering**: Raw topics partition by `{provider}:{symbol}` (or `{provider}:{symbol}:{interval}` for klines) across `6` partitions (`3` partitions on `market.anomalies.v1` and `market.dlq.v1`).
2. **Consumer Group Status**:
   - `cg.hot.redis.v1` (`[IMPLEMENTED]`): Low-latency updates to Redis via Lua monotonic timestamp guard (`HotStateProjector`).
   - `cg.analytics.clickhouse.v1` (`[IMPLEMENTED]`): Micro-batched inserts into ClickHouse `ReplacingMergeTree` tables (`ClickHouseBatchSink`).
   - `cg.lakehouse.bronze.v1` (`[IMPLEMENTED]` in v0.1 pipeline; standalone `bronze/consumer.py` CLI is `[PROP-APP-002]` stub): ZSTD Parquet flushes into Bronze storage (`BronzeParquetArchiver`).
   - `cg.anomaly.detector.v1` (`[IMPLEMENTED]`): Evaluates klines/tickers via `StatisticalAnomalyDetector` and emits breaches to `market.anomalies.v1`.
   - `cg.agent.anomaly.v1` (`[PLANNED]` standalone consumer loop): Target autonomous investigation trigger consuming `market.anomalies.v1`.

```mermaid
flowchart LR
    subgraph Producers["Producers"]
        WSCol["WebSocketStreamCollector / API Ingest"]
        RESTCol["HistoricalRestBackfillWorker"]
    end

    subgraph KafkaBroker["Apache Kafka (1-Node KRaft in Compose; 3-Broker Target PLANNED)"]
        direction TB
        subgraph TopicTrades["market.raw.trades.v1 (6 Partitions)"]
            P0["Partition 0 (e.g. binance:BTCUSDT)"]
            P1["Partition 1 (e.g. binance:ETHUSDT)"]
            PN["Partition 2..5 (Other Symbols)"]
        end
        TopicKlines["market.raw.klines.v1 (6 Partitions)"]
        TopicTickers["market.raw.tickers.v1 (6 Partitions)"]
        TopicBook["market.raw.orderbook.v1 (6 Partitions)"]
        TopicAnomaly["market.anomalies.v1 (3 Partitions)"]
        TopicDLQ["market.dlq.v1 (3 Partitions)"]
    end

    subgraph ConsumerGroups["Kafka Consumer Groups (Active in Runtime vs PLANNED Standalone)"]
        CGHot["cg.hot.redis.v1 [IMPLEMENTED]<br/>(HotStateProjector)"]
        CGCH["cg.analytics.clickhouse.v1 [IMPLEMENTED]<br/>(ClickHouseBatchSink)"]
        CGBronze["cg.lakehouse.bronze.v1 [IMPLEMENTED in Pipeline]<br/>(BronzeParquetArchiver)"]
        CGAnomaly["cg.anomaly.detector.v1 [IMPLEMENTED]<br/>(StatisticalAnomalyDetector)"]
        CGAgent["cg.agent.anomaly.v1 [PLANNED Daemon]<br/>(Cooldown-Gated Investigation Trigger)"]
    end

    subgraph Sinks["Downstream Parallel Sinks (AC-004)"]
        Redis[("Redis 7 Hot Store")]
        ClickHouse[("ClickHouse OLAP")]
        MinIO[("MinIO / .local_lakehouse Bronze")]
        AgentWorker["5-Node MarketIntelligenceGraph"]
    end

    WSCol --> TopicTrades & TopicKlines & TopicTickers & TopicBook
    RESTCol --> TopicTrades & TopicKlines
    WSCol -.->|"Malformed"| TopicDLQ

    TopicTrades & TopicKlines & TopicTickers & TopicBook --> CGHot
    TopicTrades & TopicKlines & TopicTickers & TopicBook --> CGCH
    TopicTrades & TopicKlines & TopicBook --> CGBronze
    TopicKlines & TopicTickers --> CGAnomaly

    CGHot -->|"Lua Monotonic Guard"| Redis
    CGCH -->|"Micro-Batch Insert"| ClickHouse
    CGBronze -->|"ZSTD Parquet Flush"| MinIO
    CGAnomaly -->|"Breach Detected"| TopicAnomaly
    TopicAnomaly -.-> CGAgent -.-> AgentWorker
```

