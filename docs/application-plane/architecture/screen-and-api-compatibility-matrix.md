---
doc_id: APP-ARCH-COMPAT-001
title: "Frontend Screen-to-API Compatibility & Mismatch Matrix"
doc_type: specification
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "frontend/src/app/router/router.ts"
    - "frontend/src/services/api/observability.service.ts"
    - "frontend/src/services/auth/auth.service.ts"
    - "src/serving/api/main.py"
related_docs:
  - APP-ARCH-FE-001
  - APP-ARCH-BE-001
  - CAP-APP-IAM-DOC-001
  - CAP-APP-MKT-DOC-001
  - CAP-APP-CAT-DOC-001
  - CAP-APP-OPS-DOC-001
  - CAP-APP-AGT-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Mapped every frontend screen module, backend API endpoint, SSE/WS feed, and verified contract/mock mismatches."
---

# Frontend Screen-to-API Compatibility & Mismatch Matrix

## 1. Module-to-Backend Route Mapping (`AS-IS`)

| Screen Module (`frontend/src/modules/`) | Route Hash | Frontend Service(s) Called | Backend Endpoint(s) Invoked | Owning Capability |
|---|---|---|---|---|
| **Layout Shell** (`MainLayout.ts`) | All | `auth.service.ts`, `app.store.ts` | None automatically (defaults `quant_admin`) | `CAP-APP-IAM-001`, `CAP-APP-OPS-001` |
| **Dashboard** (`DashboardModule.ts`) | `#/`, `#/dashboard` | `observability.service.ts`, `ws-client.ts`, `sse.ts` | `GET /observability/{overview,storage,latency}`, `POST /observability/{live/probe,demo/emit}`, `WS /ws/v1/observability/stream`, `GET /observability/stream` | `CAP-APP-OPS-001` |
| **Data Flow Observatory** (`DataFlowModule.ts`) | `#/data-flow` | `observability.service.ts`, `sse.ts` | `GET /observability/{topology,kafka,storage,traces,traces/{event_id},stream}`, `POST /data-platform/v01/{run,compaction}`, `POST /observability/demo/emit` | `CAP-APP-OPS-001` |
| **Market & Analytics** (`MarketAnalyticsModule.ts`) | `#/market-analytics` | `market.service.ts`, `analytics.service.ts`, `observability.service.ts` | `GET /market/{prices,orderbook/{s},snapshots/{s}}`, `GET /observability/candles`, `GET /historical/klines/{s}`, `GET /analytics/{statistics/{s},correlations,anomalies}`, `POST /analytics/anomalies/evaluate` | `CAP-APP-MKT-001` |
| **Data Management** (`DataManagementModule.ts`) | `#/data-management` | `catalog.service.ts`, `observability.service.ts`, `market.service.ts` | `GET /catalog/instruments`, `PUT /catalog/instruments/{s}`, `GET /catalog/freshness`, `POST /catalog/lakehouse/pipeline`, `GET /data-platform/v01/{watermarks,lineage,gold/{mart}}`, `GET /observability/storage` | `CAP-APP-CAT-001` |
| **AI Workspace** (`AiWorkspaceModule.ts`) | `#/ai-workspace` | `agent.service.ts` | `GET /agents/runs`, `POST /agents/runs`, `GET /agents/runs/{id}`, `GET /agents/runs/{id}/events`, `GET /reports`, `GET /reports/{id}` | `CAP-APP-AGT-001` |
| **Administration** (`AdministrationModule.ts`) | `#/administration` | `auth.service.ts`, `observability.service.ts` | `GET /platform/config`, `GET /microservices/{topology,health}`, `GET /auth/domains`, `POST /auth/api-keys`, (`GET`/`DELETE /auth/api-keys*` unimplemented!) | `CAP-APP-IAM-001`, `CAP-APP-OPS-001` |

## 2. Verified Contract & Behavior Mismatches

| Mismatch ID | Screen / Caller | Observed Backend Reality | Effect on User Experience |
|---|---|---|---|
| `COMPAT-001` | `AdministrationModule` -> `authService.getApiKeys()` | Calls `GET /api/v1/auth/api-keys` (only `POST` exists -> HTTP `405`, swallowed to `[]`). | API key list always shows empty. |
| `COMPAT-002` | `AdministrationModule` -> `authService.revokeApiKey()` | Calls `DELETE /api/v1/auth/api-keys/{id}` (route missing -> HTTP `405/404`). | Revoking API keys fails or silently errors. |
| `COMPAT-003` | `AdministrationModule` -> `createApiKey()` | Response returns `data.api_key_once`; module discards secret without showing modal/banner. | Generated secret cannot be copied by operator. |
| `COMPAT-004` | `observability.service.ts` -> `setStreamControl()` | Targets `/api/v1/observability/stream/control` (unimplemented -> HTTP `404`). | Stream pause/resume control non-functional. |
| `COMPAT-005` | `DashboardModule` Core Stores Card | Hardcodes `"5/5 Connected"` and `"min/Isolated"` trend independently of `/live/probe`. | Misleading green store status when containers are stopped. |
| `COMPAT-006` | `DataFlowModule` (`PipelineDag.ts`) | SVG nodes contain static placeholder latency/count labels outside dynamic bindings. | Stage node badges may disagree with table KPIs. |
| `COMPAT-007` | `DataManagementModule` (`CatalogService.getLineage`) | Falls back to static 8-node/4-edge array if API response empty/fails. | Masks real backend catalog errors with stale graph. |
| `COMPAT-008` | `MarketAnalyticsModule` | `|| 0.45` / `|| 0.012` / `|| 1440` fallbacks mask genuine `0` volatility/VWAP; `candles` listener rebinds duplicate `window.resize`. | False non-zero quant metrics & minor DOM memory leak. |
| `COMPAT-009` | `MicroserviceRegistry` | Advertises `/ui/data-flow` (removed `gateway/ui.py`) and `/ws/v1/market` (unimplemented). | Topology links mislead external clients into HTTP 404. |
