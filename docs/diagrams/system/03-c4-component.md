# Diagram 03: C4 Component Architecture Diagram (C4 Level 3)

## Architectural Explanation

The **C4 Component Diagram** zooms into the internal components of the three primary runtime services—**Data Collectors & Streaming Consumers**, **FastAPI Modular Backend**, and **LangGraph Agent Service**—showing how ports, adapters, domain services, and storage drivers interact across explicit boundaries.

```mermaid
flowchart TB
    subgraph IngestionWorkers["Ingestion & Streaming Worker Components"]
        BinanceWSAdapter["BinanceWebSocketClient<br/>(Reconnect, Heartbeat, Backoff)"]
        BinanceRESTAdapter["BinanceRESTClient<br/>(Rate-Limiter, Paginator)"]
        Normalizer["PayloadNormalizer<br/>(Raw JSON -> EventEnvelopeV1)"]
        SchemaValidator["ContractValidator<br/>(Pydantic Strict Validation)"]
        KafkaProducerAdapter["KafkaEventProducer<br/>(Idempotent Producer + DLQ Router)"]
        HotUpdater["HotStateProjector<br/>(Redis Lua Monotonic Writer)"]
        CHBatchWriter["ClickHouseBatchSink<br/>(1s / 5000-row Micro-Batcher)"]
        AnomalyDetector["StatisticalAnomalyDetector<br/>(Z-Score & Spread Thresholds)"]
    end

    subgraph FastAPIBackend["FastAPI Modular Monolith Components"]
        APIRouters["Presentation: Domain Routers<br/>(Market, Historical, Analytics, Catalog, IAM, Agent)"]
        AuthMiddleware["Security Middleware<br/>(JWT / API-Key RBAC & Redis Rate Limiter)"]
        MarketQueryHandler["Application: MarketQueryService<br/>(Hot Read + ClickHouse Fallback)"]
        HistQueryHandler["Application: HistoricalQueryService<br/>(Bounded Time-Range Enforcer)"]
        AnalyticsService["Application: AnalyticsQueryService<br/>(Cache-Aside + MV Query Builder)"]
        ControlService["Application: PlatformConfigService<br/>(Symbol Subscriptions & Watermarks)"]
        RedisRepo["Infrastructure: RedisMarketAdapter"]
        CHRepo["Infrastructure: ClickHouseAnalyticsAdapter"]
        PGRepo["Infrastructure: PostgresControlRepository"]
    end

    subgraph AgentService["Intelligence Plane: Agent Service Components"]
        LangGraphOrch["AgentOrchestrator<br/>(LangGraph StateGraph Engine)"]
        ToolGateway["ControlledToolGateway<br/>(Schema Validation, Timeout, RBAC, Provenance)"]
        QuantEngine["DeterministicQuantTools<br/>(Returns, Volatility, Correlation, Anomaly Check)"]
        LLMAdapter["LLMProviderAdapter<br/>(Retry, Token Accounting, Circuit Breaker)"]
        AgentStateRepo["AgentPersistenceAdapter<br/>(PostgreSQL Run & Tool Audit Store)"]
    end

    subgraph Storage["Storage & Streaming Infrastructure"]
        KafkaBroker[("Apache Kafka")]
        RedisStore[("Redis 7")]
        ClickHouseDB[("ClickHouse")]
        PostgresDB[("PostgreSQL 16")]
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

    KafkaBroker -->|"Anomaly Trigger"| LangGraphOrch
    PostgresDB -->|"On-Demand Queued Run"| LangGraphOrch
    LangGraphOrch --> LLMAdapter
    LangGraphOrch --> ToolGateway
    LangGraphOrch --> AgentStateRepo
    ToolGateway --> QuantEngine
    QuantEngine --> RedisRepo
    QuantEngine --> CHRepo
    AgentStateRepo --> PostgresDB
```

