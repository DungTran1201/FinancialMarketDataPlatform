# Non-Functional Requirements (NFR) Specification

## 1. Document Purpose & Methodology

This document defines the measurable Non-Functional Requirements (NFRs) across Performance, Scalability, Reliability, Availability, Consistency, Security, Observability, Maintainability, Testability, and Cost Efficiency.

In accordance with architectural governance rules:
- **No fabricated production SLOs**: Where exact production traffic profiles are not yet empirically measured, this specification explicitly states the **Unknown**, proposes a **Measurable Baseline Target** for the Docker Compose reference environment, defines the **Required Benchmark**, records **Assumptions**, and specifies the **Finalization Protocol**.
- All latency targets are expressed using **P50**, **P95**, and **P99** percentiles.

---

## 2. Performance Requirements

### 2.1. Latency Baseline Targets (Tier-1 Local / Single-Host Reference Profile)

| Workload / Query Category | Storage Engine | P50 Baseline | P95 Baseline | P99 Baseline | Hard API Timeout |
|---|---|---|---|---|---|
| **Hot Latest Price (`GET /market/prices/{symbol}`)** | Redis | $\le 5\text{ ms}$ | $\le 15\text{ ms}$ | $\le 30\text{ ms}$ | $1,500\text{ ms}$ |
| **Hot Market Snapshot (`GET /market/snapshots/{symbol}`)** | Redis | $\le 8\text{ ms}$ | $\le 20\text{ ms}$ | $\le 45\text{ ms}$ | $2,000\text{ ms}$ |
| **Historical Candles (`GET /historical/klines`, $\le 1000$ rows)** | ClickHouse | $\le 25\text{ ms}$ | $\le 80\text{ ms}$ | $\le 200\text{ ms}$ | $5,000\text{ ms}$ |
| **Historical Trades (`GET /historical/trades`, $\le 500$ rows)** | ClickHouse | $\le 35\text{ ms}$ | $\le 120\text{ ms}$ | $\le 300\text{ ms}$ | $5,000\text{ ms}$ |
| **Aggregated Market Statistics (Materialized View)** | ClickHouse MV / Redis | $\le 20\text{ ms}$ | $\le 75\text{ ms}$ | $\le 180\text{ ms}$ | $5,000\text{ ms}$ |
| **Multi-Symbol Correlation Matrix (30d, 1h candles, 10 pairs)** | ClickHouse | $\le 80\text{ ms}$ | $\le 250\text{ ms}$ | $\le 600\text{ ms}$ | $8,000\text{ ms}$ |
| **Control Plane CRUD (Users, Config, Agent Run Status)** | PostgreSQL | $\le 10\text{ ms}$ | $\le 30\text{ ms}$ | $\le 75\text{ ms}$ | $3,000\text{ ms}$ |
| **Agent Workflow Submission (`POST /agents/runs`)** | PostgreSQL + Queue | $\le 20\text{ ms}$ | $\le 50\text{ ms}$ | $\le 120\text{ ms}$ | $3,000\text{ ms}$ |
| **End-to-End Agent Workflow Completion (Async)** | LangGraph + LLM + Tools | $4\text{ s}$ | $15\text{ s}$ | $35\text{ s}$ | $90\text{ s}$ (Worker timeout) |

### 2.2. Ingestion & Streaming Throughput Baseline

| Metric | Baseline Target (Tier-1: 10–25 Pairs) | Scale Target (Tier-2: 200 Pairs) | Verification Benchmark |
|---|---|---|---|
| **Sustained Event Ingestion Rate** | $1,000\text{ events/sec}$ | $15,000\text{ events/sec}$ | Synthetic Kafka producer replay benchmark (`locust` / `pytest-benchmark` + custom replay script). |
| **Hot Path End-to-End Lag (Collector $\rightarrow$ Redis)** | P50 $\le 50\text{ ms}$, P95 $\le 150\text{ ms}$, P99 $\le 400\text{ ms}$ | P99 $\le 750\text{ ms}$ | Measured via `ingested_at` vs. Redis update timestamp histogram (`market_hot_path_lag_ms`). |
| **Analytics Path End-to-End Lag (Collector $\rightarrow$ ClickHouse)** | P50 $\le 1.5\text{ s}$, P95 $\le 3.0\text{ s}$, P99 $\le 5.0\text{ s}$ | P99 $\le 8.0\text{ s}$ | Governed by consumer micro-batch flush interval (`1.0s` or `5,000` events). |

---

## 3. Scalability Requirements

1. **Horizontal Partition Scalability**:
   - All Kafka topics are partitioned by `{provider}:{symbol}` (6 partitions initially, expandable to 24+ partitions).
   - Streaming consumers (Hot Cache Updater, ClickHouse Sink, Bronze Lakehouse Writer) run as stateless Kafka consumer groups that scale horizontally up to the partition count without code changes.
2. **Workload Isolation**:
   - Batch PySpark jobs, dbt transformations, and LangGraph Agent workflows run in dedicated containers/processes with explicit CPU and memory limits so they cannot starve the FastAPI event loop or real-time WebSocket collectors.
3. **Storage Growth Management**:
   - **Redis**: Bounded memory (`maxmemory 256mb` locally, `allkeys-lru` eviction on cache namespace, explicit TTLs on all keys).
   - **ClickHouse**: Partitioned monthly (`toYYYYMM(open_time)` / `toYYYYMM(trade_time)`) with ZSTD(3) compression and automated TTL rules to drop or tier raw tick data older than 90 days while retaining 1m/1h/1d candles long-term.
   - **MinIO / Iceberg**: Compaction and snapshot expiration scheduled weekly via Airflow to prevent small-file metadata explosion.

---

## 4. Reliability, Availability & Consistency Requirements

### 4.1. Delivery & Consistency Guarantees

| Path | Delivery Semantics | Consistency Model | Recovery Mechanism |
|---|---|---|---|
| **Collector $\rightarrow$ Kafka** | At-least-once (`acks=all`, `enable.idempotence=true`) | Partition-ordered | Automatic WebSocket reconnection with exponential backoff + jitter; REST gap detection and backfill trigger. |
| **Kafka $\rightarrow$ Redis** | At-least-once consumption + monotonic timestamp guard | Eventual consistency ($<500\text{ ms}$ lag) | If Redis restarts or evicts keys, next incoming event repopulates state; API falls back to ClickHouse on cache miss. |
| **Kafka $\rightarrow$ ClickHouse** | At-least-once micro-batch insert + `ReplacingMergeTree` | Eventual consistency ($1-5\text{ s}$ lag) | Consumer commits Kafka offsets only after ClickHouse batch write acknowledgement. |
| **Kafka $\rightarrow$ MinIO (Bronze)** | At-least-once append-only Parquet writes | Immutable raw log | Silver PySpark pipeline deduplicates on `(provider, symbol, natural_key)` before writing ACID Iceberg tables. |

### 4.2. Dependency Failure Matrix (Graceful Degradation)

| Failed Component | Impact on Data Ingestion | Impact on API Serving | Automated Mitigation / Fallback |
|---|---|---|---|
| **LLM Provider / Agent Service Down** | **Zero impact** | Market, Historical, and Analytics APIs remain 100% operational; only `/api/v1/agents/*` returns `503` or queues jobs. | Circuit breaker around LLM adapter; strict plane isolation. |
| **Redis Unavailable** | Collectors & ClickHouse ingestion continue unaffected. | Hot API endpoints transparently fall back to ClickHouse latest-row queries with circuit-breaker rate protection. | Readiness metric flags degraded cache mode; auto-reconnects when Redis recovers. |
| **ClickHouse Unavailable** | Kafka buffers incoming events up to retention window (72h). | Hot endpoints (`/market/prices`, `/market/snapshots`) continue serving from Redis; historical/analytical endpoints return `503`. | Kafka consumer pauses/retries with exponential backoff without losing events. |
| **MinIO / Spark / Airflow Unavailable** | Real-time Kafka, Redis, and ClickHouse paths continue 100% unaffected. | Real-time and ClickHouse historical queries remain 100% operational. | Lakehouse ingestion resumes from committed Kafka offsets / REST watermarks upon recovery. |
| **Binance WebSocket Disconnect** | Temporary gap during reconnect ($1-5\text{ s}$). | Redis serves last known price flagged with `is_stale: true` if age exceeds freshness threshold ($15\text{ s}$). | Collector reconnects with jitter and enqueues a targeted REST gap-fill for missed klines/trades. |

---

## 5. Security, Observability, Maintainability, Testability & Cost

| Category | Measurable Requirement | Architectural Mechanism |
|---|---|---|
| **Security** | Zero hardcoded secrets in repo; 100% authenticated write/agent endpoints; read-only DB credentials for Agent tools. | `.env` injection, separate PostgreSQL/ClickHouse users (`app_rw`, `analytics_ro`, `agent_ro`), query row/time-range caps. |
| **Observability** | 100% of services expose Prometheus `/metrics` and structured JSON logs with correlation IDs (`request_id`, `run_id`). | Prometheus scraping collectors, consumers, FastAPI, and Agent workers; Grafana dashboards for lag, latency, and errors. |
| **Maintainability** | Strict Clean/Hexagonal dependency direction: Domain layer has zero imports from FastAPI, SQLAlchemy, Redis, or ClickHouse SDKs. | Enforced by automated architectural boundary tests in `tests/architecture/`. |
| **Testability** | Independent execution of unit, architecture, contract, and integration tests via `pytest`. | Port/Adapter interfaces allow in-memory testing of use cases and agent tools without live external exchanges. |
| **Cost & Resource Efficiency** | Entire core stack runs on a single developer workstation ($16\text{ GB}$ RAM) via Docker Compose profiles (`core`, `lakehouse`, `observability`, `intelligence`). | Profiled Docker Compose deployment prevents running Spark/Airflow/Superset when only testing core streaming or API modules. |

---

## 6. Unknowns & Benchmark Finalization Protocol

| Unknown Parameter | Initial Baseline Assumption | Required Benchmark Test | Finalization Criterion |
|---|---|---|---|
| **Host Disk I/O Contention under Concurrent ClickHouse + Kafka + MinIO Writes** | Local NVMe SSD can sustain $1,000\text{ events/s}$ with 1s ClickHouse batching. | Run 30-minute sustained ingestion test with 25 active symbols while executing 20 concurrent Historical API queries. | Adjust ClickHouse `min_insert_block_size` and consumer flush interval (`1s` vs `5s`) so P99 API latency stays $< 200\text{ ms}$. |
| **LLM Token Cost & Latency per Anomaly Investigation** | $\le 4,000$ prompt tokens and $\le 1,500$ completion tokens per investigation run; max 6 tool calls per run. | Execute 50 synthetic anomaly investigation runs across model tiers and record token usage + wall-clock duration in `agent_runs`. | Set hard `max_tokens_per_run` and daily budget circuit breaker in `AgentOrchestrator` configuration. |

