# RealtimeFinancialMarketDataPlatform.

A production-oriented **Real-time Financial Market Data Platform** built on an **Event-Driven Data Platform with a Streaming-First Hybrid Lakehouse Architecture**, a **FastAPI Modular Monolith Backend (Clean / Hexagonal Architecture + Selective CQRS)**, and an **Isolated LangGraph Agentic Intelligence Plane**.

---

## 1. Architectural Planes Overview

1. **Plane A — Data Plane (`src/ingestion/`, `src/streaming/`, `src/lakehouse/`)**:
   - **Ingestion (`src/ingestion/`)**: Provider-isolated async WebSocket (`entrypoints/ws_collector.py`) and paginated REST (`entrypoints/rest_backfill.py`) collectors for Binance Spot (extensible via `domain/ports.py`).
   - **Event Streaming (`src/streaming/`)**: Apache Kafka (KRaft mode) partitioned by `{provider}:{symbol}` with canonical `EventEnvelopeV1` (`src/shared/contracts/events/`) and dead-letter routing (`market.dlq.v1`).
   - **Hot Data Path (`src/streaming/consumers/hot_redis.py`)**: `Kafka -> consumer-hot-redis -> Redis 7` using atomic Lua monotonic timestamp checks for sub-15ms latest price, 24h snapshot, and top-20 order book queries.
   - **Analytics Path (`src/streaming/consumers/analytics_ch.py`)**: `Kafka -> consumer-analytics-ch -> ClickHouse` using 1s / 5,000-row micro-batches into `ReplacingMergeTree` tables and `AggregatingMergeTree` Materialized Views.
   - **Historical Lakehouse Path (`src/lakehouse/`)**: `Kafka / REST -> MinIO (Parquet + Apache Iceberg) -> Bronze -> Silver -> Gold (dbt Core)` validated by `src/lakehouse/quality/gates.py` and tracked via `src/lakehouse/catalog/lineage.py`.
2. **Plane B — Serving & Control Plane (`src/serving/`)**:
   - **Modular Monolith & Microservices (`src/serving/api/`)**: FastAPI Modular Monolith (`main.py`) organized into 8 domain modules (`market`, `historical`, `analytics`, `catalog`, `iam`, `platform_config`, `agent_api`, `reporting`) plus optional standalone ASGI microservice wrappers (`services/*.py`) and Gateway/UI (`gateway/`).
   - **Control Store (`deploy/postgres/`)**: PostgreSQL 16 storing users, RBAC, API keys, monitored instruments, ingestion watermarks, and job states.
   - **BI & Observability (`deploy/observability/`)**: Apache Superset for market dashboards; Prometheus + Grafana + OpenMetrics (`src/shared/observability/metrics.py`) for operational telemetry.
3. **Plane C — Intelligence Plane (`src/intelligence/`)**:
   - **Orchestration (`src/intelligence/orchestrator/`)**: Isolated `agent-worker` (`main.py`) running stateful LangGraph workflows (`MarketIntelligenceGraph`) triggered either on-demand (`POST /api/v1/agents/runs`) or via deduplicated statistical anomalies (`market.anomalies.v1`).
   - **Controlled Tool Gateway (`src/intelligence/tools/`)**: 10 whitelisted deterministic read-only tools. LLMs never execute raw SQL or perform prompt arithmetic.

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
