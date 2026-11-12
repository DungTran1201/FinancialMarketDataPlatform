# 03 — Component Architecture (C4 Level 3)

## 1. Component Decomposition & Responsibility Boundaries

This document specifies the internal component architecture of the platform's runtime processes, ensuring that **no component has conflicting or overlapping responsibilities** and that dependency directions strictly obey Clean/Hexagonal rules.

See also: [Diagram 03: C4 Component Architecture Diagram](../diagrams/system/03-c4-component.md).

---

## 2. Data Collector & Streaming Worker Components

### 2.1. `src/collectors/` (Ingestion Components)

| Component | Interface / Port | Responsibility | Failure Handling |
|---|---|---|---|
| `BinanceWebSocketClient` | `StreamingCollectorPort` | Manages multiplexed WSS connections, subscribes to configured symbol streams, handles ping/pong keepalives, and detects sequence/time gaps on disconnect. | Reconnects with exponential backoff ($1\text{s} \rightarrow 30\text{s}$ + jitter) and emits a gap descriptor to `ingestion_watermarks`. |
| `BinanceRESTClient` | `HistoricalCollectorPort` | Executes paginated REST requests (`GET /api/v3/klines`, `/aggTrades`, `/exchangeInfo`) while tracking `X-MBX-USED-WEIGHT-*` headers. | Pauses before breaching rate limits; honours `Retry-After` on `HTTP 429`. |
| `BinanceNormalizer` | `PayloadNormalizerPort` | Translates raw Binance JSON keys (`e`, `E`, `s`, `p`, `q`, `k`) into canonical `EventEnvelopeV1` payloads with exact string `Decimal` values and UTC timestamps. | Raises `NormalizationError` caught by the DLQ router. |
| `ContractValidator` | `EventValidatorPort` | Validates every normalized event against strict Pydantic v2 contracts and computes deterministic UUIDv5 `event_id`. | Routes invalid payloads to `DeadLetterRouter` (`market.dlq.v1`) and increments `collector_validation_errors_total`. |
| `KafkaEventProducer` | `EventPublisherPort` | Serializes validated envelopes and publishes to topic-per-entity with partition key `{provider}:{symbol}`. | Uses `enable.idempotence=true`, `acks=all`, and local bounded retry queue. |

### 2.2. `src/consumers/` (Streaming Projection & Detection Components)

| Component | Consumer Group | Target Store | Responsibility & Idempotency Mechanism |
|---|---|---|---|
| `HotStateProjector` | `cg.hot.redis.v1` | Redis 7 | Updates `market:v1:price:{provider}:{symbol}`, `market:v1:snapshot:{provider}:{symbol}`, and `market:v1:orderbook:{provider}:{symbol}` via an atomic Lua script that only overwrites if `incoming.exchange_event_time >= stored.exchange_event_time`, then publishes a lightweight delta to Redis Pub/Sub for WebSocket clients. |
| `ClickHouseBatchSink` | `cg.analytics.clickhouse.v1` | ClickHouse | Accumulates in-memory columnar buffers per topic up to `1,000 ms` or `5,000 events`, executes an async bulk insert into `ReplacingMergeTree` tables, and commits Kafka offsets only upon insert success. |
| `BronzeParquetArchiver` | `cg.lakehouse.bronze.v1` | MinIO (Iceberg Bronze) | Buffers raw events up to `5 minutes` or `64 MB`, writes ZSTD-compressed Parquet files partitioned by `(provider, event_type, ingestion_date)`, and commits Kafka offsets after S3 `PutObject` verification. |
| `StatisticalAnomalyDetector` | `cg.anomaly.detector.v1` | Kafka (`market.anomalies.v1`) | Computes rolling return Z-scores, volume spikes, and bid-ask spread anomalies on closed candles/tickers; suppresses duplicate alerts via a Redis cooldown key (`15m` TTL) before emitting `MarketAnomalyEventV1`. |

---

## 3. FastAPI Modular Monolith Components (`src/backend/`)

Each domain module inside `src/backend/modules/<module_name>/` is structured into four explicit layers:

| Layer | Allowed Imports | Forbidden Imports | Key Components |
|---|---|---|---|
| `domain/` | Python standard library, `decimal`, `datetime`, `uuid`, `typing`, `src.shared.domain` | `fastapi`, `sqlalchemy`, `redis`, `clickhouse_connect`, `confluent_kafka`, `httpx`, `langgraph` | Entities (`MarketTick`, `Candle`, `Instrument`, `AgentRun`), Value Objects (`SymbolPair`, `DecimalPrice`, `TimeWindow`), Repository Port Protocols. |
| `application/` | `domain/`, `src.shared.contracts` | `fastapi`, concrete database drivers (`redis`, `clickhouse_connect`, `asyncpg`) | Query Handlers (`GetLatestPriceHandler`, `GetHistoricalCandlesHandler`), Command Handlers (`TriggerBackfillHandler`, `CreateAgentRunHandler`), DTOs. |
| `infrastructure/` | `domain/`, `application/`, database/messaging SDKs | `presentation/` (FastAPI routers) | `RedisMarketHotAdapter`, `ClickHouseAnalyticsAdapter`, `PostgresControlRepository`, `RedisCacheAsideAdapter`. |
| `presentation/` | `application/`, `domain/` (exceptions/value objects), `fastapi`, `pydantic` | Concrete `infrastructure/` repositories (injected via FastAPI `Depends` composition root) | FastAPI `APIRouter`, HTTP Request/Response schemas, Auth/RBAC and Rate-Limit dependencies. |

---

## 4. Intelligence Plane Components (`src/agent/`)

| Component | Responsibility | Isolation & Safety Boundary |
|---|---|---|
| `AgentOrchestrator` (`LangGraph`) | Manages the stateful investigation graph (`Intake -> Planner -> ToolExecutor -> Verifier -> Synthesizer`) with checkpointing in PostgreSQL. | Enforces `max_iterations = 6` and total workflow timeout of `90s`. |
| `ControlledToolGateway` | Central execution proxy for all 10 analytical and data tools. | Validates tool arguments, checks caller permissions, enforces `5s` per-tool timeout, and attaches cryptographic/structural data provenance. |
| `DeterministicQuantEngine` | Pure Python/NumPy + parameterized ClickHouse read-only queries for returns, realized volatility, correlation matrices, and Z-score anomalies. | Uses `Decimal` / `float64` deterministic math; never delegates arithmetic to the LLM. |
| `LLMProviderAdapter` | Pluggable interface (`OpenAI`, `Anthropic`, `Gemini`, `Ollama`, or `DeterministicMockAdapter`). | Tracks prompt/completion tokens, enforces per-run token budgets (`8,000` tokens), and trips a circuit breaker on repeated provider errors. |
| `ReportValidator` | Validates the synthesized report against `StructuredAnalysisReport` schema and verifies that every cited `invocation_id` exists in the current run's tool log. | Rejects fabricated citations or unverified numbers before persisting the report. |

