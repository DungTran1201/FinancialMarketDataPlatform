# Platform Technology Stack

| Metadata | Value |
|---|---|
| **Document ID** | `DOC-OVERVIEW-TECHSTACK` |
| **Title** | Polyglot Technology Stack & Infrastructure Architecture |
| **Category** | Technical Reference |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-15` |
| **Authoring Role** | `documentation-architect` |

---

## 1. Overview & Architectural Philosophy

The **FinancialMarketDataPlatform** utilizes a purpose-built polyglot technology stack where each database, streaming engine, and runtime is chosen specifically for its optimal latency, throughput, and query characteristics:

| Architectural Tier | Selected Technology | Version | Primary Purpose |
|---|---|---|---|
| **Programming Runtime** | Python | 3.12+ | Core data platform, ingestion, lakehouse engines, and serving APIs |
| **Frontend Runtime** | TypeScript / Node.js | TS 5.7+ / Node 22 | Experience layer SPA with Vite 6 build engine |
| **Streaming Backbone** | Apache Kafka / Confluent | 3.8+ / KRaft mode | High-throughput durable event pub/sub with at-least-once delivery |
| **Hot State Cache** | Redis | 7.4+ Alpine | Sub-millisecond orderbook L2 snapshots and ticker hot caching |
| **Time-Series / OLAP** | ClickHouse | 24.8+ LTS | High-concurrency columnar aggregations, VWAP, and tick analytics |
| **Medallion Lakehouse** | Apache Iceberg v2 / Parquet | ZSTD compressed | Immutable Bronze raw batches and compacted Silver/Gold tables |
| **Object Storage** | MinIO / S3 API | RELEASE.2024+ | S3-compatible cold object storage for Parquet/Iceberg layers |
| **Local Control Store** | SQLite WAL / PostgreSQL | 3.45+ / 16.4+ | Durable ingestion watermarks, sequence gap checkpoints, offset states |
| **Observability Telemetry** | Prometheus & Grafana | v2.54+ / 11.2+ | OpenMetrics exposition (`fmdp_*` SLIs), alerts, and dashboarding |
| **Reverse Proxy / Edge** | Nginx | 1.27+ Alpine | Rate limiting, TLS termination, SSE/WebSocket buffering, and routing |
| **AI Orchestration** | LangGraph | 0.2+ | Directed acyclic graph execution for autonomous investigations |

---

## 2. Polyglot Storage Tier Mapping

```text
                  Data Temperature & Latency Spectrum
  ◄───────────────────────────────────────────────────────────────────►
  HOT (Sub-ms)           WARM (1-100ms)               COLD (Analytical)
  Redis 7.4              ClickHouse 24.8              MinIO / Iceberg v2
  ─────────────────────  ──────────────────────────   ──────────────────────────
  - Top-20 Orderbook     - 1m/5m/1h/1d Klines         - Raw JSON / Bronze Parquet
  - 24h Ticker Stats     - Historical Trade Logs      - Compacted Silver Parquet
  - Sub-second Quotes    - Analytical Aggregations    - Gold Curated Marts
  - Rate Limiter Buckets - Volatility & Correlations  - Complete Audit Snapshots
```

---

## 3. Runtime Composition & Deployment Profiles

The platform supports two deployment profiles configured in `docker-compose.yml`:

1. **`core` Profile (Single-Process Modular Gateway)**:
   - Starts infrastructure dependencies (Kafka, Redis, ClickHouse, MinIO, Prometheus) and a unified single FastAPI process (`svc-api-gateway`) dispatching across all modules.
   - Ideal for local development, fast feedback, and resource-constrained environments.
2. **`microservices` Profile (8 Isolated Services)**:
   - Deploys 8 standalone microservice containers (`svc-market-hot`, `svc-historical-backfill`, `svc-analytics-quant`, `svc-catalog-governance`, `svc-iam-security`, `svc-intelligence-agent`, `svc-data-plane-v01`, and `svc-api-gateway`).
   - Enables independent scaling, healthchecks, and horizontal partitioning in production.

