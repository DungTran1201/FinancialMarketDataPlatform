# Architectural Codebase Map

| Metadata | Value |
|---|---|
| **Document ID** | `DOC-DEV-CODEBASE-MAP` |
| **Title** | Comprehensive Architectural Codebase & Module Map |
| **Category** | Developer Experience & Architecture |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-15` |
| **Authoring Role** | `documentation-architect` |

---

## 1. Top-Level Repository Architecture

```text
FinancialMarketDataPlatform/
├── src/                  # Core Data Platform, Serving & Intelligence Source Tree
├── frontend/             # Single Page Application (TypeScript / Vite / Nginx)
├── deploy/               # Deployment configs (Docker, Kafka, Nginx, Prometheus)
├── tests/                # 50 Automated tests (Unit, Contract, Integration, DQ, E2E)
├── models/               # Canonical machine-readable YAML models (38 models)
├── docs/                 # Human-readable documentation organized by 9 domains
├── work-items/           # Change lifecycle, discovery, and gate management
├── .agents/              # Agent Operating System (Roles, Rules, Skills, Configs)
└── tools/                # Automated validators & documentation engineering utilities
```

---

## 2. Source Code Breakdown (`src/`)

`src/` is structured strictly according to Clean Architecture and the 3-Plane separation (`ADR-008`):

### 2.1. `src/shared/` — Core Cross-Cutting Domain & Primitives
- `config/settings.py`: Pydantic settings loading environment variables and profiles.
- `contracts/`: Versioned event envelopes (`events/`) and dataset contracts (`schemas/`).
- `domain/quant.py`: Exact fixed-point `Decimal` financial arithmetic primitives (`BR-001`).
- `observability/`: Prometheus metrics counters, histograms, and lineage registries.
- `security/primitives.py`: JWT HS256, IP-HMAC binding, and NIST `AES-256-GCM` field masking.

### 2.2. `src/ingestion/` — Market Data Ingestion Engine
- `application/`: Stream and historical backfill orchestrators (`HistoricalRestBackfillWorker`).
- `providers/`: Exchange adapters (Binance REST/WS, Deterministic Exchange ASGI adapter).
- `infrastructure/`: Rate limiting (`TokenBucketRateLimiter`), sequence gap detection (`SequenceAndGapDetector`), SQLite WAL watermarks (`IngestionWatermarkStore`).

### 2.3. `src/streaming/` — Event Streaming & Consumers
- `consumers/`:
  - `hot_redis.py`: Sub-millisecond orderbook & ticker caching in Redis.
  - `analytics_ch.py`: High-concurrency batch flusher writing into ClickHouse.
  - `anomaly_detector.py`: Real-time Z-score anomaly detector.
- `infrastructure/`: Kafka broker adapter (`PartitionedEventStreamingBroker`, Confluent Kafka).

### 2.4. `src/lakehouse/` — Medallion Data Lakehouse
- `bronze/`: Immutable ZSTD Parquet archiver (`BronzeParquetArchiver`).
- `silver/`: Idempotent merge engine & small-file compaction (`SilverLakehouseMergeEngine`).
- `gold/`: Curated analytical mart query materialization (`GoldLayerMartEngine`).
- `quality/`: Blocking financial data quality engine (`DataQualityGateEngine`).
- `orchestration/`: 12-stage E2E data pipeline orchestrator (`DataPlatformV01Pipeline`).

### 2.5. `src/serving/` — Edge Gateway & Microservice Handlers
- `api/gateway/`: Edge routing, JWT auth middleware, and Prometheus observability metrics exporter.
- `api/modules/`: 8 Clean Architecture bounded modules (`market`, `historical`, `analytics`, `catalog`, `iam`, `platform_config`, `agent_api`, `reporting`).
- `infrastructure/runtime.py`: Service registry supporting both `IN_PROCESS_ASGI` and `REMOTE_HTTP_CONTAINER` dispatch.

### 2.6. `src/intelligence/` — Agentic AI Intelligence
- `orchestrator/`: LangGraph 6-node state graph orchestrating anomaly investigations.
- `tools/`: Controlled Tool Gateway enforcing provenance tracking.

---

## 3. Frontend Architecture (`frontend/src/`)

- `main.ts` & `index.html`: Application bootstrapping and DOM injection.
- `app/router/`: Single-page client-side router supporting 6 modules.
- `app/layouts/`: Main application layout with header, navigation sidebar, and status bar.
- `modules/`:
  - `dashboard/`: Real-time KPIs, pipeline throughput, latency, and system health cards.
  - `data-flow/`: Interactive visual SVG data flow diagram depicting the end-to-end pipeline.
  - `market-analytics/`: Candlestick charts, order book depth, and VWAP tables.
  - `data-management/`: Lakehouse partition inspection, Silver/Gold data browser.
  - `ai-workspace/`: Autonomous agent investigation triggers and provenance report viewer.
  - `administration/`: System configuration and audit logs.
- `services/`: API client (`client.ts`), WebSocket client (`ws-client.ts`), and Server-Sent Events (`sse.ts`).
- `stores/`: Reactive state management (`app.store.ts`, `market.store.ts`, `observability.store.ts`).

