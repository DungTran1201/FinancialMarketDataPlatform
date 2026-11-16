---
doc_id: APP-ARCH-001
title: "Application Plane Architecture Description"
doc_type: architecture
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/main.py"
    - "src/serving/api/gateway/registry.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - APP-ARCH-ROOT-001
  - APP-ARCH-FE-001
  - APP-ARCH-BE-001
  - DIAG-APP-C4-001
  - ADR-APP-0001
  - ADR-APP-0002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented Application Plane topology, modular monolith vs microservices execution modes, and Clean Architecture boundaries."
---

# Application Plane Architecture Description

## 1. Architectural Scope, Context & Plane Boundaries

The **Application Plane (Plane B)** delivers user-facing market telemetry, historical/analytics query APIs, catalog configuration, IAM security controls, platform operations triggers, and AI analysis portals. Per [ADR-0001](../../overview/architecture/decisions/adr-0001-three-plane-ownership-boundaries.md), Application Plane presentation modules (`src/serving/api/modules/`, `gateway/`, `services/`) delegate all Data Plane and Intelligence Plane reads/mutations through `PlatformRuntimeContainer` rather than importing lower storage adapters directly (`tests/architecture/test_clean_architecture_boundaries.py`).

```
  Browser (localhost:3000 Vite dev / Nginx SPA deploy/docker/Dockerfile.frontend)
        │  Hash SPA (#/dashboard ... #/administration)
        ▼
  Vite / Nginx Proxy (deploy/nginx/nginx.conf -> /api/*, /ws/*)
        │
        ▼
  src/serving/api/main.py (FastAPI 8000 + Security Defense Middleware)
    ├── /api/v1/auth          (IAM router; isolated in-memory JwtSecurityService)
    ├── /api/v1/market        (Market quotes, snapshots, orderbook, ingest, evict)
    ├── /api/v1/historical    (Bounded klines, trades, synchronous 202 backfill)
    ├── /api/v1/analytics     (Statistics, Pearson correlation, Z-score anomalies)
    ├── /api/v1/catalog       (Monitored instruments, freshness, lakehouse pipeline)
    ├── /api/v1/platform      (PlatformConfig + watermarks snapshot)
    ├── /api/v1/agents        (Investigation run list, sync 202 trigger, SSE stream)
    ├── /api/v1/reports       (Verified/rejected structured AI reports)
    ├── /api/v1/data-platform/v01 (12-stage orchestrator, Gold marts, lineage, metrics)
    ├── /api/v1/microservices (Topology manifest, live health, ASGI dispatch)
    └── /api/v1/observability & /ws/v1/observability/stream (Dashboard, DAG, SSE, WS)
```

## 2. Building Blocks, Constraints & Top Architectural Risks (`AS-IS`)

1. **In-Process Shared State vs Isolated Microservices**: Running `create_unified_gateway_app()` (`8000`) binds routers to one shared `PlatformRuntimeContainer`. Running standalone services (`--profile microservices`, `8001..8007`) creates isolated empty `PlatformRuntimeContainer()` instances per container with no Postgres/Redis shared backing.
2. **Router Authentication Gap (`SEC-AUDIT-001/003`)**: `install_security_defense_middleware` inspects Host headers, regex WAF patterns, and IP rate limits on `main.py` and `services/iam.py`, but zero domain endpoints verify Bearer JWT tokens or enforce `ROLE_CAPABILITIES`.
3. **Synchronous `202 Accepted` Execution**: `POST /market/ingest`, `POST /historical/backfill-jobs`, and `POST /agents/runs` execute full pipelines synchronously inside the ASGI request handler before returning HTTP `202`.
4. **Dead / Unimplemented Gateway Surface**: `MicroserviceRegistry` advertises `/ui/data-flow` (nonexistent `gateway/ui.py` -> 404) and `/ws/v1/market` (unimplemented across `src/`).
5. **Frontend Auth Mismatch**: `frontend/src/services/auth/auth.service.ts` defaults any unauthenticated browser session to `quant_admin` (`ADMIN`) without login UI or JWT token handling.
