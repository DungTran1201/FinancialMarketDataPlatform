# 02 — System Container Architecture (C4 Level 2)

## 1. Container Topology Across the Three Planes

The platform is composed of modular, single-responsibility containers grouped into the **Data Plane**, **Application & Control Plane**, **Intelligence Plane**, and **Observability & Governance Plane**.

See also: [Diagram 02: C4 Container Architecture Diagram](../diagrams/system/02-c4-container.md).

---

## 2. Container Inventory & Ownership Matrix (`docker-compose.yml` vs. Planned Targets)

The table below distinguishes **deployable containers defined in `docker-compose.yml`** (`IMPLEMENTED` / `PARTIALLY_IMPLEMENTED` stub entrypoints) from **conceptual target batch containers** (`PLANNED`, not in `docker-compose.yml`). See also `models/deployment/deployment.yaml`.

| Container Name | Plane | Technology | Scaling Model | Statefulness | Implementation Status | Primary Responsibility |
|---|---|---|---|---|---|---|
| `collector-ws` | Data Plane | Python 3.12+ (`src.ingestion.entrypoints.ws_collector`) | Sharded by symbol group | Stateless | `PARTIALLY_IMPLEMENTED` (CLI startup stub; normalizer in-process) | Maintains live Binance WebSocket stream consumption (`BinancePayloadNormalizer`). |
| `collector-rest` | Data Plane | Python 3.12+ (`src.ingestion.entrypoints.rest_backfill`) | Worker pool | Stateless | `PARTIALLY_IMPLEMENTED` (CLI startup stub; `ProductionExchangeHistoricalCollector` active in-process) | Executes paginated `exchangeInfo` / historical kline fetches and watermarked gap-fills. |
| `kafka` | Data Plane | Apache Kafka (KRaft mode) | 1 node locally (3-broker target) | Stateful (`kafka_data` volume) | `IMPLEMENTED` (Compose `core`/`lakehouse`/`intelligence`) | Durable event log partitioned by `{provider}:{symbol}`. |
| `consumer-hot-redis` | Data Plane | Python 3.12+ (`src.streaming.consumers.hot_redis`) | Horizontal up to partition count | Stateless | `IMPLEMENTED` (Lua projector active in-process & standalone CLI) | Consumes market streams and executes atomic Lua monotonic state updates in Redis. |
| `consumer-analytics-ch` | Data Plane | Python 3.12+ (`src.streaming.consumers.analytics_ch`) | Horizontal up to partition count | Stateless | `IMPLEMENTED` (micro-batch sink active in-process & standalone CLI) | Buffers events (`1s` or `5,000` rows) for ClickHouse `ReplacingMergeTree` batch inserts. |
| `consumer-lakehouse-bronze` | Data Plane | Python 3.12+ (`src.lakehouse.bronze.consumer`) | Horizontal up to partition count | Stateless | `PARTIALLY_IMPLEMENTED` (CLI startup stub; `BronzeParquetArchiver` runs in-process) | Buffers raw event envelopes and writes immutable ZSTD Parquet files to `.local_lakehouse/bronze` (MinIO target). |
| `redis` | Data Plane | Redis 7 Alpine | Single primary locally | Ephemeral (`256MB`, `volatile-lru`) | `IMPLEMENTED` (Compose `core`/`intelligence`) | Serves hot market prices, snapshots, top-20 order books, and caches. |
| `clickhouse` | Data Plane | ClickHouse Server 24.x (`:8123` HTTP, `:9000` Native) | Single node locally | Stateful (`clickhouse_data` volume) | `IMPLEMENTED` (Compose `core`/`lakehouse`/`intelligence`/`bi`) | Serves historical candles, trades, and analytical OLAP tables (`market_data.*`). |
| `minio` | Data Plane | MinIO Server (`:9010->9000` S3 API, `:9001` Console) | Single node locally | Stateful (`minio_data` volume) | `PARTIALLY_IMPLEMENTED` (Compose `lakehouse` infra ready; active lakehouse writes to `.local_lakehouse/`) | Object storage backend target for Bronze, Silver, and Gold Parquet/Iceberg datasets (`lakehouse-*` buckets). |
| `backend-api` | Application & Control Plane | FastAPI + Uvicorn (Python 3.12+, `:8000`) | Stateless replicas | Stateless | `IMPLEMENTED` (Compose `core`, 55 HTTP/WS/SSE routes) | Modular Monolith serving `/api/v1/*`, `/ws/v1/observability/stream`, `/metrics`, and `/api/v1/microservices/*`. |
| `svc-market-hot`..`svc-data-plane-v01` (7 services) | Planes A, B, C | FastAPI + Uvicorn (`:8001`..`:8007`) | Independent per domain | Stateless | `IMPLEMENTED` (Compose `microservices` profile) | Optional decomposed ASGI apps (`src/serving/api/services/*.py`) dispatched over ASGI in-process or HTTP in Compose. |
| `frontend` | Experience Layer | Vite + TypeScript SPA (`node`, host `:3001->3000`) | Stateless frontend | Stateless | `IMPLEMENTED` (Compose `core`/`frontend` profile) | Multi-module web UI (`/dashboard`, `/data-flow`, `/market-analytics`, `/data-management`, `/ai-workspace`, `/administration`). |
| `edge-gateway` | Access Boundary | Nginx TLS 1.3 Reverse Proxy (`:80`, `:443`) | Stateless proxy | Stateless | `IMPLEMENTED` (Compose `core` profile) | Terminates HTTPS (`*.fmdp.local`), enforces edge rate limits, proxies `backend-api`, `frontend`, `grafana`, `superset`, `minio`. |
| `postgres` | Application & Control Plane | PostgreSQL 16 Alpine (`:5432`) | Primary | Stateful (`postgres_data` volume) | `IMPLEMENTED` (Compose `core`/`lakehouse`/`intelligence`/`bi`) | Relational schema (`deploy/postgres/init/01_schema.sql`) for IAM, instruments, watermarks, audit logs, and Agent runs. |
| `superset` | Application & Control Plane | Apache Superset (`:8088`) | Stateless web UI | Metadata in PG | `PARTIALLY_IMPLEMENTED` (Compose `bi` container defined; dashboards/sync `PLANNED`) | Interactive BI visualization target over ClickHouse views. |
| `agent-worker` | Intelligence Plane | Python 3.12+ (`src.intelligence.main`) | Worker pool | Checkpoints in PG | `PARTIALLY_IMPLEMENTED` (CLI startup stub; 5-node `MarketIntelligenceGraph` runs via API) | Isolated container target for async `cg.agent.anomaly.v1` Agent runs. |
| `prometheus` | Observability Plane | Prometheus Server (`:9090`) | Single instance | Stateful (`prometheus_data` volume) | `PARTIALLY_IMPLEMENTED` (Compose `observability`; scrapes `backend-api:8000/metrics` & `svc-data-plane-v01:8007`) | Collects `fmdp_*` counters/histograms and evaluates `alerts.yml`. |
| `grafana` | Observability Plane | Grafana OSS (`:3000`) | Stateless UI | Provisioned datasource | `PARTIALLY_IMPLEMENTED` (Compose `observability`; datasource provisioned, prebuilt JSON dashboards `PLANNED`) | Visualization UI connected to Prometheus datasource. |
| `spark-worker` | Data Plane *(Logical Target)* | Apache Spark / PySpark 3.5 | Ephemeral batch container | Stateless | `PLANNED` (**Not in `docker-compose.yml`**; in-process `SilverLakehouseMergeEngine` active) | Target distributed Bronze $\rightarrow$ Silver deduplication and compaction runner. |
| `dbt-runner` | Data Plane *(Logical Target)* | dbt Core (`dbt-clickhouse`) | Ephemeral batch container | Stateless | `PLANNED` (**Not in `docker-compose.yml`**; `src/lakehouse/gold/dbt/` project skeleton + Python `GoldLayerMartEngine` active) | Target SQL transformation runner for Gold marts. |
| `great-expectations` | Data Plane *(Logical Target)* | Great Expectations Runner | Ephemeral batch container | Stateless | `PLANNED` (**Not in `docker-compose.yml`**; Python `Decimal` `DataQualityGateEngine` active) | Target external GE checkpoint suite runner. |
| `airflow` | Data Plane *(Logical Target)* | Apache Airflow 2.x | Scheduler + Worker | Metadata in PG | `PLANNED` (**Not in `docker-compose.yml`**; `DataPlatformV01Pipeline` active) | Target scheduled batch orchestrator for backfills, dbt, and GE suites. |

---

## 3. Inter-Container Communication Protocols & Contracts

| Source Container | Target Container | Protocol | Payload Format | Sync / Async | Resilience & Backpressure Mechanism |
|---|---|---|---|---|---|
| `collector-ws` / `collector-rest` | `kafka` | Kafka Binary TCP (`:9092`) | JSON (`EventEnvelopeV1`, `acks=all`) | Async Batched | `ConfluentKafkaStreamingAdapter` / `PartitionedEventStreamingBroker` with `event_id` deduplication. |
| `kafka` | `consumer-*` | Kafka Consumer Group Protocol | JSON (`EventEnvelopeV1`) | Async Pull | Consumer group rebalance, manual offset commit after sink acknowledgement (`cg.agent.anomaly.v1` `PLANNED`). |
| `consumer-hot-redis` | `redis` | RESP3 TCP (`:6379`) | Pipelined `EVAL` / `EVALSHA` (Lua) | Async Pipelined | Atomic timestamp guard (`exchange_event_time_ms`), reconnect backoff. |
| `consumer-analytics-ch` | `clickhouse` | HTTP / Native (`:8123` / `:9000`) | Columnar batch insert | Async Micro-Batch ($1\text{ s}$ / $5{,}000$ rows) | Retries batch insert before advancing Kafka offset (`ReplacingMergeTree`). |
| `backend-api` | `redis` | RESP3 TCP (`:6379`) | Hash/JSON Read | Sync Non-Blocking (`asyncio`) | Transparent fallback to ClickHouse on miss/timeout/error (`TC-003`). |
| `backend-api` | `clickhouse` | HTTP Async (`:8123`) | Parameterized SQL | Sync Non-Blocking (`asyncio`) | Bounded time-range guardrooms, partition pruning (`ReplacingMergeTree`). |
| `backend-api` | `postgres` | PostgreSQL Wire (`:5432`) | Parameterized SQL (`asyncpg`) | Sync Non-Blocking (`asyncio`) | Control-plane metadata (`monitored_instruments`, `ingestion_watermarks`, `agent_runs`). |
| `agent-worker` / `MarketIntelligenceGraph` | `ControlledToolGateway` | In-Process Typed Tool Calls | Python DTOs (`10` approved tools) | Async Bounded ($5\text{ s}$ timeout) | Tool whitelist, RBAC permission check, row caps (`max <= 500/720/2160/168`), provenance audit log (`fmdp_agent_ro` DB role `PLANNED`). |
| `agent-worker` / `MarketIntelligenceGraph` | External LLM API | HTTPS TLS 1.3 (`:443`) / Mock | JSON Chat/Tool Completions | Async Bounded | Token cap (`AGENT_MAX_TOKENS_PER_RUN=8000`), step cap (`max_iterations=6`), deterministic offline fallback (`DeterministicMockLLMAdapter`). |

