# Work Item Request — `ARCH-001`: Event-Driven Modular Data Platform Restructure

## 1. Request Summary

Reorganize and standardize `FinancialMarketDataPlatform` according to an **Event-Driven Modular Data Platform** architecture:
- Separate `src/` cleanly by architectural responsibility and plane boundary: `shared/`, `ingestion/`, `streaming/`, `lakehouse/`, `serving/`, and `intelligence/`.
- Standardize `deploy/` (`docker/`, `kafka/`, `postgres/`, `clickhouse/`, `object-storage/`, `iceberg/`, `observability/`, plus retained edge security `nginx/` and `tls/`).
- Introduce machine-readable Data Platform governance models under `models/data-platform/` (`datasets.yaml`, `events.yaml`, `topics.yaml`, `quality-rules.yaml`, `lineage.yaml`, `retention.yaml`).
- Reorganize `tests/` by verification concern (`architecture/`, `unit/`, `contract/`, `integration/`, `data_quality/`, `e2e/`, `resilience/`, `performance/`).
- Synchronize `docs/`, `docs/diagrams/`, `models/`, ADRs (`ADR-008`), `.agents/` configs, scripts (`setup.bat`, `run.bat`, `docker-compose.yml`, `.github/workflows/ci.yml`), and directory READMEs.

## 2. Hard Constraints

1. Preserve existing business logic and runtime behavior (only refactor imports, boundaries, and placement).
2. No fake placeholder files or doc-only architectures; every directory must contain cohesive, real components.
3. No duplicated module copies/shims to preserve legacy paths; migrate all callers cleanly.
4. Preserve working entrypoints and deployment profiles (`core`, `intelligence`, `lakehouse`, `observability`, `bi`, `microservices`).
5. Keep Serving API as a Modular Monolith (`src/serving/api/modules/`) while keeping optional isolated microservice ASGI entrypoints (`src/serving/api/services/` + `src/serving/api/gateway/`).

