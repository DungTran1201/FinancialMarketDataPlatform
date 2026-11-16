---
doc_id: APP-ARCH-BE-001
title: "Backend Architecture (FastAPI Serving & Microservice Wrappers)"
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
    - "src/serving/api/gateway/service.py"
    - "src/serving/api/gateway/observability.py"
    - "src/serving/api/services/iam.py"
related_docs:
  - APP-ARCH-ROOT-001
  - APP-ARCH-001
  - APP-ARCH-DATA-001
  - DIAG-APP-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented FastAPI composition root, 12 router mounts, standalone microservice factories, and Clean Architecture enforcement."
---

# Backend Architecture (FastAPI Serving & Microservice Wrappers)

## 1. Scope & Context: Unified Composition Root (`src/serving/api/main.py`)

`create_unified_gateway_app()` instantiates one `PlatformRuntimeContainer` (with auto-closing `watermark_store` SQLite connection in FastAPI `lifespan`), installs `install_security_defense_middleware(app)`, and mounts:

| Prefix | Factory Function | Backing Module / Gateway |
|---|---|---|
| `/` | `root_service_index` | `src/serving/api/main.py` |
| `/api/v1/health/live`, `/ready` | Inline handlers | `src/serving/api/main.py` (unauthenticated; always returns `ready` without probing DBs) |
| `/metrics` | `export_prometheus_metrics` | `src/serving/api/main.py` (`PlainTextResponse`, `fmdp_*` text) |
| `/api/v1/auth` | `build_iam_security_router` | `src/serving/api/modules/iam/presentation/router.py` |
| `/api/v1/market` | `build_market_router` | `src/serving/api/modules/market/presentation/router.py` |
| `/api/v1/historical` | `build_historical_router` | `src/serving/api/modules/historical/presentation/router.py` |
| `/api/v1/analytics` | `build_analytics_router` | `src/serving/api/modules/analytics/presentation/router.py` |
| `/api/v1/catalog` | `build_catalog_router` | `src/serving/api/modules/catalog/presentation/router.py` |
| `/api/v1/platform` | `build_platform_config_router` | `src/serving/api/modules/platform_config/presentation/router.py` |
| `/api/v1/agents` | `build_agent_api_router` | `src/serving/api/modules/agent_api/presentation/router.py` |
| `/api/v1/reports` | `build_reporting_router` | `src/serving/api/modules/reporting/presentation/router.py` |
| `/api/v1/data-platform/v01` | `build_data_platform_v01_router` | `src/serving/api/services/data_plane.py` |
| `/api/v1/microservices` | `build_microservices_gateway_router` | `src/serving/api/gateway/service.py` |
| `/api/v1/observability` | `build_observability_router` | `src/serving/api/gateway/observability.py` |
| `/ws/v1/observability/stream` | `build_observability_ws_router` | `src/serving/api/gateway/observability.py` |

## 2. Building Blocks: Microservice Wrappers & Divergence Risks

`src/serving/api/services/{market,historical,analytics,catalog,iam,intelligence,data_plane}.py` define standalone FastAPI apps on ports `8001..8007` (with Gateway on `8000`):
- **Middleware Divergence**: Only `main.py` (`8000`) and `services/iam.py` (`8005`) install `install_security_defense_middleware`. Calling `8001..8004`, `8006`, `8007` directly bypasses Host header, WAF regex, HSTS/CSP headers, and rate limits.
- **State Divergence**: Even inside `main.py`, `services/iam.py` creates its own isolated `JwtSecurityService` and `SlidingWindowRateLimiter`. And under Compose `--profile microservices`, each service instantiates an isolated empty `PlatformRuntimeContainer()`.
- **Dead Routes in Registry**: `gateway/registry.py` references `/ui/data-flow` (`gateway/ui.py` does not exist) and `/ws/v1/market` on `svc-market-hot` (no route defined).
- **Latency / Blocking Risk**: `POST /market/ingest`, `POST /historical/backfill-jobs`, and `POST /agents/runs` execute work inline with `await` inside request handlers prior to returning HTTP `202`, lacking a background worker queue (`Celery`/`ARQ`/`asyncio.create_task` + persistence).
