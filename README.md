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

## 2. Documentation & Repository Index

> **Documentation Phase Notice**: This repository operates on **Documentation V2 — Phase 1: Documentation Foundation**. Phase 2 project specifications (`docs/overview/`, `docs/data-plane/`, `docs/application-plane/`, `docs/intelligence-plane/`) are intentionally reserved and have not yet been authored.

### Documentation V2 Foundation (`docs/`)
- [AGENTS.md — Root AI Agent Documentation Contract](AGENTS.md)
- [docs/README.md — Documentation V2 Master Entrypoint & Reading Order](docs/README.md)
- [docs/docs-index.yaml — Machine-Readable Documentation & Plane Index](docs/docs-index.yaml)
- [docs/governance/README.md — Governance, Standards, Catalog, Schemas & Templates](docs/governance/README.md)
- [docs/governance/migration/legacy-inventory.md — Legacy Documentation V1 Inventory Audit](docs/governance/migration/legacy-inventory.md)
- [docs/governance/migration/legacy-disposition.md — Legacy Cleanup & Tag Preservation Record](docs/governance/migration/legacy-disposition.md)

### Code, Infrastructure & Verification Subsystems
- [src/ — Modular Data Platform Source Layout](src/README.md)
- [deploy/ — Infrastructure, Schema, Bucket & Observability Configs](deploy/README.md)
- [tests/ — Multi-Discipline Automated Verification Suites](tests/README.md)
- [.agents/ — Agent Lifecycle Hook Configuration](.agents/README.md)
- [tools/ — Compatibility Validation & Hook Wrappers](tools/README.md)

---

## 3. Running Architectural, Test & Documentation Verification Suites

```powershell
# Run All Test Suites via Pytest (Unit, Contract, Architecture, Data Quality, Integration, E2E, Resilience, Performance, Docs)
.\.venv\Scripts\python.exe -m pytest -v

# Run Clean Architecture & Platform Unit Tests via unittest
.\.venv\Scripts\python.exe -m unittest discover -s tests -v

# Run Documentation V2 Schema, Applicability, Link & Traceability Validator
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py

# Compatibility Documentation Validator Entrypoint
.\.venv\Scripts\python.exe tools/validators/run_all.py

# Lint Source Code, Tests & Documentation Tooling Scripts
.\.venv\Scripts\ruff.exe check src tests scripts tools
```
