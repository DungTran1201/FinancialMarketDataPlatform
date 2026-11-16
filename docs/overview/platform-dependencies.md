---
doc_id: OVR-DEP-001
title: "Platform Software, Infrastructure & Cross-Plane Dependencies"
doc_type: specification
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "pyproject.toml"
    - "frontend/package.json"
    - "docker-compose.yml"
related_docs:
  - OVR-ROOT-001
  - OVR-ARCH-3P-001
  - GOV-MIG-P2AUD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Cataloged declared vs actually imported software dependencies and Docker container services."
---

# Platform Software, Infrastructure & Cross-Plane Dependencies

## 1. Python Dependencies (`pyproject.toml`, Python `>=3.12`)

| Dependency | Extra Group | Declared Purpose | Actual Usage in `src/` (`AS-IS`) |
|---|---|---|---|
| `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings` | Core | HTTP gateway, routers, settings schema | Actively imported in `src/serving/` & embedded exchange ASGI simulator (`pydantic` un-used in most `dict` Body endpoints) |
| `httpx` | Core | Async HTTP client & ASGI transport | Actively imported in `ProductionExchangeHistoricalCollector` and `MicroserviceRegistry` |
| `prometheus-client`, `cryptography`, `pyyaml`, `pyarrow` | Core | Metrics, AES-256-GCM, config YAML, local ZSTD Parquet | Actively imported in `src/shared/` & `src/lakehouse/` |
| `websockets`, `confluent-kafka`, `redis`, `clickhouse-connect`, `sqlalchemy`, `asyncpg` | Core | Live WS, Kafka, Redis, ClickHouse, Postgres async IO | **Zero active runtime calls** in `PlatformRuntimeContainer`; only lazy optional `confluent_kafka` helper exists in `kafka_broker.py` |
| `pyiceberg[s3fs]`, `pyspark`, `dbt-core`, `dbt-clickhouse`, `great-expectations` | `lakehouse` | Distributed Iceberg/Spark/dbt/GE pipelines | **Not installed by `Dockerfile.python`** (`pip install --no-cache-dir .`); zero imports in `src/`. Offline `dbt parse` artifacts exist under `src/lakehouse/gold/dbt/target/` |
| `langgraph`, `numpy` | `intelligence` | Graph orchestration & numeric arrays | **Not installed by `Dockerfile.python`**; zero imports in `src/` (`MarketIntelligenceGraph` uses pure Python) |
| `pytest`, `pytest-asyncio`, `ruff`, `jsonschema` | `dev` / `docs` | Automated testing, linting & Documentation V2 validation | Actively used in `tests/` and `scripts/docs/validate_docs.py` |

## 2. Frontend Dependencies (`frontend/package.json`)

- **Runtime dependencies**: **None** (zero third-party runtime UI libraries; vanilla TypeScript + Canvas + SVG).
- **Dev dependencies**: `typescript ^5.7.0`, `vite ^6.0.0`, `@types/node ^22.0.0`. (Note: host shell lacks Node/npm; TypeScript build/test commands execute in `Dockerfile.frontend` `node:22-alpine`.)

## 3. Infrastructure Dependencies (`docker-compose.yml` — 24 Declared Services)

- **`core` profile (10)**: `postgres:16-alpine` (`:5432`), `redis:7.2-alpine` (`:6379`), `apache/kafka:3.7.0` (`:9092`), `clickhouse/clickhouse-server:24.3-alpine` (`:8123`, `:9000`), `backend-api` (`:8000`), `frontend` (`:3001->3000`), `edge-gateway` (`nginx:1.27-alpine`, `:80`, `:443`), plus exit-immediately stub workers `collector-ws`, `collector-rest`, `consumer-hot-redis`, `consumer-analytics-ch`. (Note `clickhouse` also belongs to `lakehouse`, `intelligence`, `bi`.)
- **`lakehouse` profile**: `minio/minio:latest` (`:9000`, `:9001`), stub `consumer-lakehouse-bronze` (`MINIO_ENDPOINT` vs `MINIO_ENDPOINT_URL` mismatch). **Missing from Compose**: `iceberg-rest:8181` referenced in `deploy/iceberg/catalog-config.yaml`.
- **`intelligence` profile**: stub `agent-worker` (`python -m src.intelligence.main`).
- **`observability` profile**: `prom/prometheus:v2.52.0` (`:9090`), `grafana/grafana:11.0.0` (`:3000`, datasource YAML not mounted).
- **`bi` profile**: `apache/superset:3.1.3` (`:8088`, unconfigured).
- **`microservices` profile (7)**: `svc-market-hot` (`:8001`), `svc-historical-backfill` (`:8002`), `svc-analytics-quant` (`:8003`), `svc-catalog-governance` (`:8004`), `svc-iam-security` (`:8005`), `svc-intelligence-agent` (`:8006`), `svc-data-plane-v01` (`:8007`).

## 4. Shared Kernel Module Coupling Rules

Enforced automatically by [test_clean_architecture_boundaries.py](../../tests/architecture/test_clean_architecture_boundaries.py):
- `src/shared/` -> external stdlib/libraries ONLY (zero imports from any FMDP subsystem).
- `src/ingestion/`, `src/streaming/`, `src/intelligence/` -> MAY import `src/shared/` ONLY (plus `bronze -> streaming/ingestion` or orchestrated via `orchestration/pipeline.py` & `runtime.py`).
- `*/domain/*.py` -> pure Python stdlib + `src/shared/domain/` ONLY (zero FastAPI, SQLAlchemy, Redis, Kafka, HTTP, or LLM SDK imports).
