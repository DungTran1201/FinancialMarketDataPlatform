# Diagram 05: Data Ingestion Architecture

## Architectural Explanation

The **Data Ingestion Architecture** details how both real-time WebSocket streams and paginated REST historical endpoints are ingested reliably:
- **Symbol Subscription Sync**: Collectors load active symbol configurations (`BTCUSDT`, `ETHUSDT`, etc.) from PostgreSQL on startup and refresh periodically.
- **WebSocket Resilience**: `collector-ws` maintains multiplexed connections, tracks heartbeat pings/pongs, reconnects with exponential backoff + jitter on disconnect, and records any timestamp gap so `collector-rest` can backfill missed klines/trades.
- **Normalization & Validation Gate**: Raw exchange JSON is mapped through a provider-specific adapter (`BinanceNormalizer`) into the canonical `EventEnvelopeV1` Pydantic contract with a deterministic UUIDv5 `event_id` before publishing to Kafka. Malformed payloads are isolated in `market.dlq.v1`.

```mermaid
flowchart TB
    subgraph External["Binance Exchange APIs"]
        BWS["Binance WebSocket Stream<br/>wss://stream.binance.com:9443"]
        BREST["Binance REST API v3<br/>https://api.binance.com/api/v3"]
    end

    subgraph ControlDB["Configuration & State (PostgreSQL)"]
        InstTable[("monitored_instruments<br/>Active Symbols & Streams")]
        WatermarkTable[("ingestion_watermarks<br/>Last Synced Timestamps")]
    end

    subgraph WSWorker["collector-ws (Real-Time Ingestion Worker)"]
        ConnMgr["WebSocketConnectionManager<br/>(TLS, Ping/Pong, Exponential Backoff)"]
        GapTracker["SequenceAndGapDetector<br/>(Detects Disconnection Windows)"]
        WSNorm["BinanceStreamNormalizer<br/>(Decimal Conversion & UTC Normalization)"]
    end

    subgraph RESTWorker["collector-rest (Historical & Gap-Fill Worker)"]
        RateLimiter["TokenBucketRateLimiter<br/>(Respects X-MBX-USED-WEIGHT)"]
        Paginator["TimeRangePaginator<br/>(1000-Row Chunk Fetcher)"]
        RESTNorm["BinanceRESTNormalizer<br/>(Canonical Envelope Builder)"]
    end

    subgraph ValidationGate["Contract Validation & Producer Layer"]
        Validator["PydanticContractValidator<br/>(EventEnvelopeV1 + Deterministic UUIDv5)"]
        IdempProducer["IdempotentKafkaProducer<br/>(acks=all,linger.ms=5,compression=lz4)"]
    end

    subgraph KafkaCluster["Apache Kafka Topics"]
        TTrades[("market.raw.trades.v1")]
        TKlines[("market.raw.klines.v1")]
        TTickers[("market.raw.tickers.v1")]
        TBook[("market.raw.orderbook.v1")]
        TDLQ[("market.dlq.v1")]
    end

    InstTable -->|"Load Subscribed Pairs"| ConnMgr
    InstTable -->|"Load Backfill Scope"| Paginator
    WatermarkTable <-->|"Read / Advance Watermark"| Paginator

    BWS -->|"Stream Events"| ConnMgr
    ConnMgr --> GapTracker
    GapTracker -.->|"Record Gap Window"| WatermarkTable
    GapTracker --> WSNorm

    BREST -->|"Paginated JSON"| RateLimiter
    RateLimiter --> Paginator
    Paginator --> RESTNorm

    WSNorm --> Validator
    RESTNorm --> Validator

    Validator -->|"Valid Canonical Event"| IdempProducer
    Validator -.->|"Schema Violation"| TDLQ

    IdempProducer -->|"Key: provider:symbol"| TTrades
    IdempProducer -->|"Key: provider:symbol:interval"| TKlines
    IdempProducer -->|"Key: provider:symbol"| TTickers
    IdempProducer -->|"Key: provider:symbol"| TBook
```

