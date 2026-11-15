# Implementation Plan — FEAT-001

| Metadata | Value |
|---|---|
| **Work Item ID** | `FEAT-001` |
| **Authoring Role** | `documentation-architect` |
| **Status** | `COMPLETED` |
| **Created Date** | `2026-11-15` |
| **Updated Date** | `2026-11-15` |

---

## 1. Sequenced Execution Stages

1. **Stage 1 — Shared Tracing & Metrics (`src/shared/observability/`)**: Create `tracing.py` (`EventLifecycleTrace`, `PipelineTraceRegistry`, percentile stats, parallel branch aggregation) and expand `metrics.py` with bounded-label histograms/counters.
2. **Stage 2 — Broker, OLAP & Pipeline Introspection (`src/streaming/`, `src/lakehouse/`)**: Add read-only partition/offset/lag/timeseries snapshots in `kafka_broker.py`, `Decimal` OHLCV interval rollups (`5m`, `15m`, `1h`, `4h`, `1d`) & table stats in `analytics_ch.py`, and trace hooks in `pipeline.py`.
3. **Stage 3 — Runtime Wiring & Clean Facade (`src/serving/infrastructure/runtime.py`)**: Expose observability overview, topology (including honest Broker 2/3 & external infra probe status), Kafka snapshot, Iceberg/Parquet/ClickHouse storage explorer, candlestick query wrapper, trace inspector, `LIVE` probe trigger, and `DEMO` fault/burst simulator.
4. **Stage 4 — Security CSP & Gateway Routes (`src/serving/api/`)**: Scope `/ui/*` CSP safely in `iam/presentation/router.py`, build `gateway/observability.py` (`/api/v1/observability/*` + SSE), add WebSocket `/ws/v1/observability/stream`, and build static assets + HTML shell in `gateway/ui.py` & `gateway/static/`.
5. **Stage 5 — Canonical Models, Docs & Diagrams**: Update `models/`, `docs/specifications/api-specification.md`, `docs/product/11-ux/`, `docs/diagrams/ux/01-realtime-data-flow-ui-architecture.md`, and author `docs/product/13-operations/monitoring.md`.
6. **Stage 6 — Automated Tests & Live Verification**: Run `ruff`, `unittest`, `pytest` (including `tests/integration/test_realtime_observability_dashboard.py`), `tools/validators/run_all.py`, and live HTTP server verification.

## 2. Dependencies & Preconditions

- Existing Python 3.12 `.venv` with FastAPI, Uvicorn, PyArrow, Prometheus client, httpx, pytest, and ruff installed.
- `tests/architecture/test_clean_architecture_boundaries.py` green before and after every code change.

## 3. Rollback & Recovery Strategy

- New observability endpoints live purely under `/api/v1/observability/*` and `/ws/v1/observability/*`; legacy `/api/v1/data-platform/v01/*` routes remain intact and backward-compatible.
- Any failure in SSE/WS/UI isolates cleanly inside `src/serving/api/gateway/` without impacting Plane A ingestion, Kafka partitioning, or Lakehouse Parquet/Iceberg durability.
