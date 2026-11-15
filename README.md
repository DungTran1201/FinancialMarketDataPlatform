# RealtimeFinancialMarketDataPlatform.

A production-oriented **Real-time Financial Market Data Platform** built on an **Event-Driven Data Platform with a Streaming-First Hybrid Lakehouse Architecture**, a **FastAPI Modular Monolith Backend (Clean / Hexagonal Architecture + Selective CQRS)**, and an **Isolated LangGraph Agentic Intelligence Plane**.

---

## 1. Architectural Planes Overview

> [!NOTE]
> **Implementation Status (`AS-IS`)**: The unified FastAPI Modular Monolith (`55` routes), Data Platform v0.1 in-process 12-stage engines (`BronzeParquetArchiver`, `SilverLakehouseMergeEngine`, `GoldLayerMartEngine`, `DataQualityGateEngine`), 5-node LangGraph orchestrator (`10` tools), TypeScript/Vite SPA (`frontend/`), and 8 ASGI domain microservices (`svc-*`) are **`IMPLEMENTED`**. Standalone daemon worker loops (`ws_collector.py`, `rest_backfill.py`, `bronze/consumer.py`, `intelligence/main.py`; `PROP-APP-002`), MinIO S3 upload vs `.local_lakehouse` Parquet default, distributed Spark/Airflow/GE batch execution, `WS /ws/v1/market/stream`, and per-route domain RBAC (`PROP-APP-004`) remain **`PARTIALLY_IMPLEMENTED` / `PLANNED`**.

1. **Plane A — Data Plane (`src/ingestion/`, `src/streaming/`, `src/lakehouse/`)**:
   - **Ingestion (`src/ingestion/`)**: Binance REST/WS normalizers, `TokenBucketRateLimiter`, `SequenceAndGapDetector`, and SQLite/PG watermarks (`entrypoints/*.py` CLI daemons are config-logging startup stubs in v0.1).
   - **Event Streaming (`src/streaming/`)**: Apache Kafka (KRaft) partitioned by `{provider}:{symbol}` with canonical `EventEnvelopeV1` (`src/shared/contracts/events/`) and dead-letter routing (`market.dlq.v1`).
   - **Hot Data Path (`src/streaming/consumers/hot_redis.py`)**: `HotStateProjector` monotonic timestamp guard (`BR-003`) targeting Redis 7 hot state + ClickHouse fallback.
   - **Analytics Path (`src/streaming/consumers/analytics_ch.py`)**: `ClickHouseBatchSink` targeting ClickHouse `ReplacingMergeTree` tables and `AggregatingMergeTree` Materialized Views (`deploy/clickhouse/init/`).
   - **Historical Lakehouse Path (`src/lakehouse/`)**: `BronzeParquetArchiver` -> `SilverLakehouseMergeEngine` -> `GoldLayerMartEngine` (`dbt` model stubs under `src/lakehouse/gold/dbt/`) validated by `DataQualityGateEngine` (`DQ-KLINE-001..005`, `DQ-TRADE-001..003`) and tracked via `DataLineageGovernanceRegistry` (writes locally to `.local_lakehouse`; MinIO `lakehouse-*` buckets provisioned).
2. **Plane B — Serving & Control Plane (`src/serving/`)**:
   - **Modular Monolith & Microservices (`src/serving/api/`)**: FastAPI Modular Monolith (`main.py`, `55` routes) organized into 8 domain modules plus opt-in standalone ASGI microservice wrappers (`services/*.py`), Gateway (`gateway/`), and TypeScript/Vite frontend (`frontend/`, host port `3001`).
   - **Control Store (`deploy/postgres/`)**: PostgreSQL 16 DDL (`01_schema.sql`) and local SQLite watermark store (`IngestionWatermarkStore`).
   - **BI & Observability (`deploy/observability/`)**: Apache Superset (`--profile bi`), Prometheus + Grafana (`--profile observability`), and OpenMetrics (`10` `fmdp_*` metrics in `src/shared/observability/metrics.py`).
3. **Plane C — Intelligence Plane (`src/intelligence/`)**:
   - **Orchestration (`src/intelligence/orchestrator/`)**: Stateful **5-node** LangGraph workflow (`MarketIntelligenceGraph`) invoked via `/api/v1/agents/runs` (`agent-worker` CLI stub in `main.py`).
   - **Controlled Tool Gateway (`src/intelligence/tools/`)**: `10` whitelisted deterministic read-only tools (`BR-004`). LLMs never execute raw SQL or perform prompt arithmetic.

---

## 2. Documentation Index

### Architecture Documents (`docs/architecture/`)
- [00 — Architecture Overview & Implementation Roadmap](docs/architecture/00-architecture-overview.md)
- [01 — System Context Architecture (C4 Level 1)](docs/architecture/01-system-context.md)
- [02 — System Container Architecture (C4 Level 2)](docs/architecture/02-system-container-architecture.md)
- [03 — Component Architecture (C4 Level 3)](docs/architecture/03-component-architecture.md)
- [04 — Data Platform Architecture & 12-Stage Data Lifecycle](docs/architecture/04-data-platform-architecture.md)
- [05 — Backend Architecture (Modular Monolith, Hexagonal, CQRS)](docs/architecture/05-backend-architecture.md)
- [06 — Agentic Intelligence Architecture (LangGraph & Tool Gateway)](docs/architecture/06-agentic-intelligence-architecture.md)
- [07 — Data Storage and Modeling (ClickHouse, Iceberg, Redis, PostgreSQL)](docs/architecture/07-data-storage-and-modeling.md)
- [08 — Data Flow and Event Contracts](docs/architecture/08-data-flow-and-event-contracts.md)
- [09 — API and Integration Architecture](docs/architecture/09-api-and-integration-architecture.md)
- [10 — Security and Governance Architecture](docs/architecture/10-security-and-governance.md)
- [11 — Reliability and Observability Architecture](docs/architecture/11-reliability-and-observability.md)
- [12 — Deployment Architecture (Docker Compose Profiles)](docs/architecture/12-deployment-architecture.md)
- [13 — Performance and Scalability Architecture](docs/architecture/13-performance-and-scalability.md)
- [14 — Data Platform v0.1 & Domain Microservices Architecture](docs/architecture/14-data-platform-v01-and-microservices-architecture.md)

### Architecture Decision Records (`docs/architecture/adr/`)
- [ADR-001 — Overall Three-Plane Architecture](docs/architecture/adr/ADR-001-overall-architecture.md)
- [ADR-002 — Event-Driven Data Platform & Streaming vs. Batch Boundaries](docs/architecture/adr/ADR-002-event-driven-data-platform.md)
- [ADR-003 — Polyglot Storage Strategy & Workload Separation](docs/architecture/adr/ADR-003-storage-strategy.md)
- [ADR-004 — Modular Monolith Backend with Clean/Hexagonal Architecture & Selective CQRS](docs/architecture/adr/ADR-004-backend-architecture.md)
- [ADR-005 — High-Performance Query Routing & Tiered Caching Strategy](docs/architecture/adr/ADR-005-query-and-caching-strategy.md)
- [ADR-006 — Isolated Agentic Intelligence Plane & Deterministic Tool Gateway](docs/architecture/adr/ADR-006-agent-integration.md)
- [ADR-007 — Zero-Mock Data Platform v0.1 & Domain Microservices Decomposition](docs/architecture/adr/ADR-007-microservices-and-data-platform-v01.md)
- [ADR-008 — Event-Driven Modular Data Platform Restructure](docs/architecture/adr/ADR-008-event-driven-modular-data-platform.md)

### Specifications (`docs/specifications/`)
- [Data Requirements Specification](docs/specifications/data-requirements.md)
- [Data Dictionary Specification](docs/specifications/data-dictionary.md)
- [Data Contracts Specification](docs/specifications/data-contracts.md)
- [API Specification](docs/specifications/api-specification.md)
- [Non-Functional Requirements (NFR) Specification](docs/specifications/non-functional-requirements.md)

### Subsystem & Governance Indexes
- [src/ — Modular Data Platform Source Layout](src/README.md)
- [deploy/ — Infrastructure, Schema, Bucket & Observability Configs](deploy/README.md)
- [tests/ — Multi-Discipline Automated Verification Suites](tests/README.md)
- [AGENTS.md — Primary Agent Operating Manual](AGENTS.md)
- [.agents/ — Agent Governance OS (Roles, Rules, Skills, Registries, Hooks)](.agents/README.md)
- [docs/ — Master Documentation System Index](docs/README.md)
- [docs/product/ — 15-Phase Product Documentation Lifecycle (`00-discovery` .. `14-governance`)](docs/product/README.md)
- [docs/templates/ — 57 Reusable Document Templates across 14 Categories](docs/templates/README.md)
- [docs/features/ — Reusable Feature Package Engineering Pattern](docs/features/README.md)
- [docs/diagrams/ — Unified 18-Category Diagram Engineering Subsystem](docs/diagrams/README.md)
- [models/ — Canonical Machine-Readable YAML Model Layer (13 Domains)](models/README.md)
- [work-items/ — Work-Item Lifecycle Control Subsystem (`DOCS-001`)](work-items/README.md)
- [tools/ — Automated Validation Suite & Hook Scripts](tools/README.md)

---

## 3. Running Architectural & Documentation Verification Suites

```powershell
# Run All Test Suites via Pytest (Unit, Contract, Architecture, Data Quality, Integration, E2E, Resilience, Performance)
.\.venv\Scripts\python.exe -m pytest -v

# Run Clean Architecture & Platform Unit Tests via unittest
.\.venv\Scripts\python.exe -m unittest discover -s tests -v

# Run Automated Documentation & Traceability Validation Suite
.\.venv\Scripts\python.exe tools/validators/run_all.py

# Lint Source Code & Tests
.\.venv\Scripts\ruff.exe check src tests
```
