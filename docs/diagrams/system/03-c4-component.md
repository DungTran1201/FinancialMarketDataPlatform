# Diagram 03: C4 Component Architecture Diagram (C4 Level 3) (`DIAG-C4-003`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-C4-003` |
| **Title** | C4 Component Architecture Diagram (C4 Level 3) |
| **Diagram Category** | `docs/diagrams/system/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart TB)` |
| **Status** | `IMPLEMENTED` / `PARTIALLY_IMPLEMENTED` (in-process runtime active; non-IAM RBAC `[PROP-APP-004]` and standalone worker daemon loops `[PROP-APP-002]` pending) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/00-architecture-overview.md`, `docs/architecture/05-backend-architecture.md` |
| **Canonical Model Reference** | `models/architecture/components.yaml` |
| **Related Artifact IDs** | `COMP-001`..`COMP-020`, `PROP-APP-002`, `PROP-APP-004` |

## Architectural Explanation

The **C4 Component Diagram** zooms into the internal components of the three primary runtime layers—**Ingestion & Streaming Workers**, **FastAPI Modular Backend** (all **8** domain modules plus Gateway Observability), and **Intelligence Plane Service**—showing how ports, adapters, domain services, and storage drivers interact across explicit boundaries.

```mermaid
flowchart TB
    subgraph IngestionWorkers["Ingestion & Streaming Components (src/ingestion & src/streaming)"]
        BinanceWSAdapter["WebSocketStreamCollector<br/>(Reconnect, Gap Detection, Backoff)"]
        BinanceRESTAdapter["HistoricalRestBackfillWorker<br/>(TokenBucketRateLimiter, Paginator)"]
        Normalizer["BinancePayloadNormalizer<br/>(Raw JSON -> EventEnvelopeV1)"]
        SchemaValidator["Pydantic ContractValidator<br/>(Strict Decimal & UUIDv5 Checks)"]
        KafkaProducerAdapter["PartitionedEventStreamingBroker<br/>(6 Partitions + market.dlq.v1)"]
        HotUpdater["HotStateProjector<br/>(Redis Lua Monotonic Writer)"]
        CHBatchWriter["ClickHouseBatchSink<br/>(Micro-Batch & OLAP Aggregations)"]
        AnomalyDetector["StatisticalAnomalyDetector<br/>(Z-Score & Spread Thresholds)"]
    end

    subgraph FastAPIBackend["FastAPI Modular Monolith Components (src/serving/api/)"]
        APIRouters["Presentation: 8 Domain Modules + Observability<br/>(Market, Historical, Analytics, Catalog, IAM, Config, Agents, Reports)"]
        AuthMiddleware["Security Defense Middleware<br/>(In-Memory SlidingWindowRateLimiter & Cipher; Non-IAM RBAC: PROP-APP-004 PLANNED)"]
        MarketQueryHandler["Application: GetLatestPriceHandler<br/>(Hot Read + ClickHouse Fallback)"]
        HistQueryHandler["Application: HistoricalQueryService<br/>(Bounded Time-Range Enforcer)"]
        AnalyticsService["Application: AnalyticsQueryService<br/>(Aggregated Metrics & Anomalies)"]
        ControlService["Application: PlatformConfigService<br/>(Symbol Subscriptions & Watermarks)"]
        RedisRepo["HotStateProjector / Redis Adapter"]
        CHRepo["ClickHouseBatchSink / OLAP Adapter"]
        PGRepo["Watermark & Control Repository"]
    end

    subgraph AgentService["Intelligence Plane: 5-Node Agent Service (src/intelligence/)"]
        LangGraphOrch["MarketIntelligenceGraph<br/>(5-Node Orchestrator)"]
        ToolGateway["ControlledToolGateway<br/>(10 Whitelisted Tools, Timeout, Row Caps, Provenance)"]
        QuantEngine["DeterministicQuantTools<br/>(Returns, Volatility, Correlation, Anomaly Check)"]
        LLMAdapter["LLM Narrative Adapter<br/>(Configurable External LLM + Deterministic Fallback)"]
        AgentStateRepo["Agent Run & Evidence State Store"]
    end

    subgraph Storage["Storage & Streaming Infrastructure"]
        KafkaBroker[("Apache Kafka KRaft")]
        RedisStore[("Redis 7")]
        ClickHouseDB[("ClickHouse")]
        PostgresDB[("PostgreSQL 16 / SQLite")]
    end

    BinanceWSAdapter --> Normalizer
    BinanceRESTAdapter --> Normalizer
    Normalizer --> SchemaValidator
    SchemaValidator --> KafkaProducerAdapter
    KafkaProducerAdapter --> KafkaBroker

    KafkaBroker --> HotUpdater
    KafkaBroker --> CHBatchWriter
    KafkaBroker --> AnomalyDetector
    HotUpdater --> RedisStore
    CHBatchWriter --> ClickHouseDB
    AnomalyDetector -->|"Publish market.anomalies.v1"| KafkaBroker

    APIRouters --> AuthMiddleware
    AuthMiddleware --> MarketQueryHandler
    AuthMiddleware --> HistQueryHandler
    AuthMiddleware --> AnalyticsService
    AuthMiddleware --> ControlService

    MarketQueryHandler --> RedisRepo
    MarketQueryHandler -.->|"Fallback on Miss/Down"| CHRepo
    HistQueryHandler --> CHRepo
    AnalyticsService --> RedisRepo
    AnalyticsService --> CHRepo
    ControlService --> PGRepo

    RedisRepo --> RedisStore
    CHRepo --> ClickHouseDB
    PGRepo --> PostgresDB

    KafkaBroker -.->|"Anomaly Trigger [PLANNED Daemon]"| LangGraphOrch
    PostgresDB -->|"On-Demand / Agent State"| LangGraphOrch
    LangGraphOrch --> LLMAdapter
    LangGraphOrch --> ToolGateway
    LangGraphOrch --> AgentStateRepo
    ToolGateway --> QuantEngine
    QuantEngine --> RedisRepo
    QuantEngine --> CHRepo
    AgentStateRepo --> PostgresDB
```

