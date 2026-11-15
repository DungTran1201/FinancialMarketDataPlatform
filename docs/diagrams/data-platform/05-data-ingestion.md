# Diagram 05: Data Ingestion Architecture (`DIAG-DATA-005`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-DATA-005` |
| **Title** | Data Ingestion Architecture |
| **Diagram Category** | `docs/diagrams/data-platform/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart TB)` |
| **Status** | `IMPLEMENTED` / `PARTIALLY_IMPLEMENTED` (REST backfill & normalization active in v0.1 pipeline; standalone worker daemons `[PROP-APP-002]` pending) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/04-data-platform-architecture.md`, `docs/architecture/08-data-flow-and-event-contracts.md` |
| **Canonical Model Reference** | `models/process/processes.yaml` |
| **Related Artifact IDs** | `FR-01`, `FR-02`, `FR-03`, `PROC-001`, `PROP-APP-002` |

## Architectural Explanation

The **Data Ingestion Architecture** details how real-time WebSocket streams and paginated REST historical endpoints are ingested reliably:
- **Symbol Subscription & Watermark State**: Active configuration/watermark stores use SQLite WAL (`src/ingestion/infrastructure/watermark_store.py`) locally and PostgreSQL control schema in Docker Compose (`monitored_instruments`, `ingestion_watermarks`).
- **WebSocket & REST Workers**: `WebSocketStreamCollector` tracks sequence gaps via `SequenceAndGapDetector`; `HistoricalRestBackfillWorker` obeys Binance `X-MBX-USED-WEIGHT-1M` headers via `TokenBucketRateLimiter`. Note `[PROP-APP-002]`: standalone Compose CLI entrypoints (`ws_collector.py`, `rest_backfill.py`) are currently stubs while active ingestion runs via `backend-api` / `svc-data-plane-v01`.
- **Normalization & Validation Gate**: Raw exchange JSON is mapped via `BinancePayloadNormalizer` into `EventEnvelopeV1` with deterministic UUIDv5 `event_id` and published to Kafka (1-node KRaft in Compose; malformed payloads routed to `market.dlq.v1`).

```mermaid
flowchart TB
    subgraph External["Binance Exchange APIs"]
        BWS["Binance WebSocket Stream<br/>wss://stream.binance.com:9443"]
        BREST["Binance REST API v3<br/>https://api.binance.com/api/v3"]
    end

    subgraph ControlDB["Configuration & Watermark State (SQLite WAL / PostgreSQL)"]
        InstTable[("monitored_instruments<br/>Active Symbols & Streams")]
        WatermarkTable[("ingestion_watermarks<br/>Last Synced Timestamps")]
    end

    subgraph WSWorker["WebSocketStreamCollector (Pipeline / CLI Stub PROP-APP-002)"]
        ConnMgr["WebSocketConnectionManager<br/>(TLS, Ping/Pong, Exponential Backoff)"]
        GapTracker["SequenceAndGapDetector<br/>(Detects Disconnection Windows)"]
        WSNorm["BinancePayloadNormalizer<br/>(Decimal Conversion & UTC Normalization)"]
    end

    subgraph RESTWorker["HistoricalRestBackfillWorker (Active HTTP Client & Pipeline)"]
        RateLimiter["TokenBucketRateLimiter<br/>(Respects X-MBX-USED-WEIGHT-1M)"]
        Paginator["TimeRangePaginator<br/>(1000-Row Chunk Fetcher)"]
        RESTNorm["BinancePayloadNormalizer<br/>(Canonical Envelope Builder)"]
    end

    subgraph ValidationGate["Contract Validation & Producer Layer"]
        Validator["ContractValidator<br/>(EventEnvelopeV1 + Deterministic UUIDv5)"]
        IdempProducer["PartitionedEventStreamingBroker / Producer<br/>(Key Partitioning + DLQ Routing)"]
    end

    subgraph KafkaCluster["Apache Kafka Topics (1-Node KRaft in Compose)"]
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

