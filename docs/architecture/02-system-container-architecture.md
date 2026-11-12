# 02 — System Container Architecture (C4 Level 2)

## 1. Container Topology Across the Three Planes

The platform is composed of modular, single-responsibility containers grouped into the **Data Plane**, **Application & Control Plane**, **Intelligence Plane**, and **Observability & Governance Plane**.

See also: [Diagram 02: C4 Container Architecture Diagram](../diagrams/system/02-c4-container.md).

---

## 2. Container Inventory & Ownership Matrix

| Container Name | Plane | Technology | Scaling Model | Statefulness | Primary Responsibility |
|---|---|---|---|---|---|
| `collector-ws` | Data Plane | Python 3.12+ (`asyncio`, `websockets`, `confluent-kafka`) | Sharded by symbol group | Stateless (watermarks in PG) | Maintains persistent Binance WebSocket connections, normalizes payloads, validates schemas, and publishes to Kafka. |
| `collector-rest` | Data Plane | Python 3.12+ (`httpx`, `confluent-kafka`) | Worker pool / Airflow task | Stateless (watermarks in PG) | Polls `exchangeInfo`, executes paginated historical kline/trade backfills, and fills WebSocket disconnection gaps. |
| `kafka` | Data Plane | Apache Kafka (KRaft mode) | Broker cluster (1 node locally) | Stateful (`kafka_data` volume) | Durable event log partitioned by `{provider}:{symbol}`; decouples ingestion from hot, OLAP, Lakehouse, and anomaly consumers. |
| `consumer-hot-redis` | Data Plane | Python 3.12+ (`confluent-kafka`, `redis.asyncio`) | Horizontal up to partition count | Stateless | Consumes `trades`, `tickers`, `klines`, `orderbook` and executes atomic Lua monotonic state updates + Pub/Sub fan-out in Redis. |
| `consumer-analytics-ch` | Data Plane | Python 3.12+ (`confluent-kafka`, `clickhouse-connect`) | Horizontal up to partition count | Stateless (offset committed post-flush) | Buffers events (`1s` or `5,000` rows) and performs asynchronous bulk columnar inserts into ClickHouse base tables. |
| `consumer-lakehouse-bronze` | Data Plane | Python 3.12+ (`pyarrow`, `pyiceberg` / `s3fs`) | Horizontal up to partition count | Stateless (offset committed post-write) | Buffers raw event envelopes (`5m` or `64MB`) and writes immutable ZSTD Parquet files to MinIO Bronze storage. |
| `redis` | Data Plane | Redis 7 Alpine | Single primary locally | Ephemeral In-Memory (`256MB` cap) | Serves sub-15ms hot market prices, snapshots, top-20 order books, sliding-window rate limits, and short-TTL query caches. |
| `clickhouse` | Data Plane | ClickHouse Server 24.x | Vertical + Shard/Replica ready | Stateful (`clickhouse_data` volume) | Serves historical candles, trades, Materialized View aggregations, Superset BI queries, and deterministic Agent quant queries. |
| `minio` | Data Plane | MinIO Server (S3 API) | Distributed object storage ready | Stateful (`minio_data` volume) | Stores Bronze, Silver, and Gold Apache Parquet files and Apache Iceberg metadata/manifests. |
| `spark-worker` | Data Plane | Apache Spark / PySpark 3.5 | Ephemeral batch container | Stateless | Executes scheduled Bronze $\rightarrow$ Silver deduplication, schema standardization, historical merges, and Iceberg compaction. |
| `dbt-runner` | Data Plane | dbt Core (`dbt-clickhouse` / `dbt-spark`) | Ephemeral batch container | Stateless | Transforms Silver tables and ClickHouse base tables into curated Gold analytical marts. |
| `great-expectations` | Data Plane | Great Expectations Python Runner | Ephemeral batch container | Stateless | Executes automated data quality checkpoint suites against ClickHouse and Silver/Gold Iceberg tables. |
| `airflow` | Data Plane | Apache Airflow 2.x | Scheduler + Triggerer + Worker | Metadata in PostgreSQL | Orchestrates scheduled historical backfills, PySpark jobs, dbt transformations, and Great Expectations validations. |
| `backend-api` | Application & Control Plane | FastAPI + Uvicorn (Python 3.12+) | Horizontally scalable stateless replicas | Stateless | Modular Monolith serving `/api/v1/*` REST, `/ws/v1/*` WebSocket, and SSE endpoints with RBAC and rate limiting. |
| `postgres` | Application & Control Plane | PostgreSQL 16 Alpine | Primary + Read-replica ready | Stateful (`postgres_data` volume) | System of record for users, RBAC, API keys, monitored symbols, ingestion watermarks, Airflow metadata, and Agent runs. |
| `superset` | Application & Control Plane | Apache Superset | Stateless web service | Metadata in PostgreSQL | Provides interactive BI dashboards and visual analytics over ClickHouse read-only views. |
| `agent-worker` | Intelligence Plane | Python 3.12+ (`langgraph`, `httpx`, `pydantic`) | Horizontally scalable worker pool | Checkpoints in PostgreSQL | Executes asynchronous on-demand and anomaly-triggered LangGraph workflows via the Controlled Tool Gateway. |
| `prometheus` | Observability Plane | Prometheus Server | Single instance locally | Stateful (`prometheus_data` volume) | Scrapes `/metrics` endpoints from collectors, consumers, FastAPI, Agent workers, Kafka, Redis, and ClickHouse. |
| `grafana` | Observability Plane | Grafana OSS | Stateless UI | Provisioned dashboards | Renders operational dashboards for ingestion throughput, consumer lag, API P50/P95/P99 latency, and Agent token usage. |

---

## 3. Inter-Container Communication Protocols & Contracts

| Source Container | Target Container | Protocol | Payload Format | Sync / Async | Resilience & Backpressure Mechanism |
|---|---|---|---|---|---|
| `collector-ws` / `collector-rest` | `kafka` | Kafka Binary TCP (`:9092`) | JSON (`EventEnvelopeV1`, LZ4 compressed) | Async Batched (`linger.ms=5`) | Bounded local producer queue (`queue.buffering.max.messages=100000`), idempotent retries (`acks=all`). |
| `kafka` | `consumer-*` | Kafka Consumer Group Protocol | JSON (`EventEnvelopeV1`) | Async Pull | Consumer group rebalance, manual offset commit after sink acknowledgement, pause/resume backpressure. |
| `consumer-hot-redis` | `redis` | RESP3 TCP (`:6379`) | Pipelined `EVALSHA` (Lua) + `PUBLISH` | Async Pipelined | Atomic timestamp comparison; reconnect backoff on socket drop. |
| `consumer-analytics-ch` | `clickhouse` | HTTP / Native (`:8123` / `:9000`) | Columnar batch insert | Async Micro-Batch ($1\text{ s}$) | Retries batch insert with exponential backoff before advancing Kafka offset. |
| `backend-api` | `redis` | RESP3 TCP (`:6379`) | Hash/JSON Read (`HGETALL`, `GET`) | Sync Non-Blocking (`asyncio`) | $500\text{ ms}$ socket timeout; automatic fallback to ClickHouse on timeout/error. |
| `backend-api` | `clickhouse` | HTTP Async (`:8123`) | Parameterized SQL (`readonly=1`) | Sync Non-Blocking (`asyncio`) | $5\text{ s}$ query timeout, `max_rows_to_read` guard, connection pool cap. |
| `backend-api` | `postgres` | PostgreSQL Wire (`:5432`) | Parameterized SQL (`asyncpg`) | Sync Non-Blocking (`asyncio`) | SQLAlchemy `AsyncEngine` pool (`pool_size=10`), transactional rollback on error. |
| `agent-worker` | `redis` / `clickhouse` | Via In-Process `ToolGateway` | Typed Python Tool DTOs | Async Bounded ($5\text{ s}$ timeout) | Read-only credentials (`agent_ro`), strict row limits, provenance tagging. |
| `agent-worker` | External LLM API | HTTPS TLS 1.3 (`:443`) | JSON Chat/Tool Completions | Async Bounded ($30\text{ s}$ per call) | Token budget cap, max 2 retries, circuit breaker, deterministic fallback error report. |

