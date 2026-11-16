---
doc_id: OVR-ARCH-SYS-001
title: "Platform System Architecture Overview"
doc_type: architecture
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/main.py"
    - "src/serving/infrastructure/runtime.py"
    - "src/lakehouse/orchestration/pipeline.py"
    - "docker-compose.yml"
related_docs:
  - OVR-ROOT-001
  - OVR-ARCH-3P-001
  - OVR-DIAG-CONT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Documented system-wide container architecture, runtime composition roots, and AS-IS vs TARGET structural differences."
---

# Platform System Architecture Overview

Derived views: [c4-container.md](../diagrams/c4-container.md) (`DIAG-OVR-CONT-001`) and [deployment-context.md](../diagrams/deployment-context.md) (`DIAG-OVR-DEP-001`).

## 1. Architectural Scope, Goals & Constraints `[REQUIRED]`

- **Scope**: End-to-end runtime topology across ingress, frontend SPA, backend API monolith / 7 domain ASGI sub-apps, data processing stages, intelligence orchestrator, and declared container storage stack.
- **Constraints**: Clean Architecture domain purity (`tests/architecture/test_clean_architecture_boundaries.py`), fixed-point `Decimal` math (`DecimalPrice`), and zero silent mutation outside documented APIs.

## 2. System Context & External Boundaries `[REQUIRED]`

Refer to [system-context.md](../system-context.md) (`OVR-CTX-001`): browser clients enter through Vite dev proxy (`:3000`) or Docker Edge Nginx (`:80 -> :443` `fmdp.local` -> `frontend:3000` / `backend-api:8000`). External market ingestion targets Binance Spot APIs (`wss://stream.binance.com:9443/ws`, `https://api.binance.com/api/v3`).

## 3. Building Block & Container Structure `[REQUIRED]`

| Building Block / Container | Responsibility (`AS-IS` Code Reference) | Allowed Dependencies | Prohibited Dependencies |
|---|---|---|---|
| `frontend` (`nginx:1.27-alpine` / Vite `:3000`) | Hash SPA (`frontend/src/app/router/router.ts`) serving 6 views | `backend-api` via `/api/v1/*`, `/ws/v1/*` | Direct connections to DBs, Kafka, Redis, or ClickHouse |
| `edge-gateway` (`nginx:1.27-alpine` `:80/:443`) | TLS termination, host routing (`fmdp.local`, `monitor.`, `bi.`, `console.s3.`), edge rate limits (`deploy/nginx/nginx.conf`) | Proxies to `frontend`, `backend-api`, `grafana`, `superset`, `minio` | Direct DB queries |
| `backend-api` (`src/serving/api/main.py`) | Composition host running `PlatformRuntimeContainer`, middleware, gateway, observability SSE/WS, 8 REST routers & DataPlatformV01 triggers | `src/shared/`, Data Plane engines, Intelligence orchestrator | Unauthenticated mutations (`BLOCKED` gap `SEC-AUDIT-003`) |
| `svc-*` Microservice Wrappers (`services/*.py`) | 7 optional standalone FastAPI factories (`:8001..:8007`) under `--profile microservices` | `src/shared/` + own module routers | In-process memory sharing across separate containers (`GAP-ARCH-001`) |
| Data Plane Workers (`collector-*`, `consumer-*`) | Stub container entrypoints in `docker-compose.yml` vs active in-process engines inside `DataPlatformV01Pipeline` | `src/shared/`, upstream topics/watermarks | Direct imports of `src/serving/` or `src/intelligence/` |
| `agent-worker` (`src/intelligence/main.py`) | Stub worker entrypoint vs in-process `MarketIntelligenceGraph` + `ControlledToolGateway` | Invokes read/report handlers only via `ControlledToolGateway` | Raw SQL execution or unbounded LLM tool invocation |

## 4. Runtime & Cross-Cutting Concepts

- **Composition Roots**: Two explicit composition roots exist: `PlatformRuntimeContainer` (`src/serving/infrastructure/runtime.py`) and `DataPlatformV01Pipeline` (`src/lakehouse/orchestration/pipeline.py`).
- **Observability & Telemetry**: Every ingested/demo/pipeline event updates `PipelineTraceRegistry` (`t0`–`t9`) and `DataObservabilityMetricsCollector` (Prometheus registry exported at `GET /metrics`).

## 5. Current Implementation (`AS-IS`) vs. Target Architecture (`TARGET`) `[REQUIRED]`

| Component | `AS-IS` Reality (`7880c85`) | `TARGET` Design Intent | Migration Gap |
|---|---|---|---|
| **Backend Execution** | Single `backend-api` monolith runs Data + App + Intelligence Planes in-process with memory dicts + SQLite + `.local_lakehouse/`. | Decoupled `backend-api` (or persisted domain services), standalone worker consumers (`kafka`/`redis`/`clickhouse`/`postgres`), MinIO S3, and real exchange connectors. | `GAP-ARCH-001`, `GAP-DATA-001` |
| **Security Enforcement** | Edge Host/WAF/rate-limit middleware runs, but auth tokens are self-verified and domain endpoints lack JWT/RBAC guards (`SEC-AUDIT-001..005`). | Postgres-backed user credential & API key verification, Bearer/key enforcement on all protected routes, CIDR-validated `X-Forwarded-For`, non-default secrets. | `SEC-AUDIT-001..005` (`BLOCKED`) |
| **LLM & External Storage** | `DeterministicMockLLMAdapter`; `use_embedded_asgi_transport=True` Binance simulator. | Configurable external LLM provider behind strict `ControlledToolGateway`; live Binance WS/REST + live Kafka/Redis/ClickHouse/Postgres/MinIO. | `OPEN-PROD-003`, `GAP-DATA-001` |

## 6. Linked Decisions & Risks `[REQUIRED]`

- **ADRs**: [adr-0001](decisions/adr-0001-three-plane-ownership-boundaries.md), [adr-0002](decisions/adr-0002-modular-monolith-vs-microservices-runtime.md) (`DRAFT` — unresolved), [adr-0003](decisions/adr-0003-decimal-precision-and-deterministic-tool-gateway.md).
- **Risk Register**: [phase-2-risk-and-gap-register.md](../../governance/migration/phase-2-risk-and-gap-register.md).
