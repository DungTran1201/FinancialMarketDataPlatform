---
doc_id: APP-ARCH-FE-001
title: "Frontend Architecture (TypeScript Vite SPA)"
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
    - "frontend/src/main.ts"
    - "frontend/src/app/router/router.ts"
    - "frontend/src/app/layouts/MainLayout.ts"
    - "frontend/vite.config.ts"
related_docs:
  - APP-ARCH-ROOT-001
  - APP-ARCH-COMPAT-001
  - ADR-APP-0001
  - DIAG-APP-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented vanilla TypeScript SPA architecture, routing, reactive stores, transport adapters, and verified UI gaps."
---

# Frontend Architecture (TypeScript Vite SPA)

## 1. Scope, Context, Framework & Routing Topology (`AS-IS`)

- **Stack**: Zero-framework vanilla TypeScript ES2022 bundled by Vite (`frontend/vite.config.ts`, dev port `3000`, Docker build via `deploy/docker/Dockerfile.frontend` output `dist/`).
- **Proxy Config**: Dev server forwards `/api/*` -> `VITE_API_TARGET` (`http://127.0.0.1:8000` default) and `/ws/*` -> WebSocket equivalent (`ws://127.0.0.1:8000`). Production edge uses `deploy/nginx/nginx.conf`.
- **Router (`frontend/src/app/router/router.ts:26-34`)**: Hash-based SPA router defaulting to `#/dashboard` with zero authentication or RBAC guards:
  - `#/` and `#/dashboard` -> `DashboardModule.ts`
  - `#/data-flow` -> `DataFlowModule.ts`
  - `#/market-analytics` -> `MarketAnalyticsModule.ts`
  - `#/data-management` -> `DataManagementModule.ts`
  - `#/ai-workspace` -> `AiWorkspaceModule.ts`
  - `#/administration` -> `AdministrationModule.ts`
- **Layout (`frontend/src/app/layouts/MainLayout.ts`)**: Renders top bar (`LIVE/DEMO` toggle, theme switch, notifications counter button) and sidebar navigation across the 6 modules.

## 2. Building Blocks: State Stores, Services & Reusable Components

- **Stores (`frontend/src/stores/`)**: Lightweight observer pattern stores (`app.store.ts`, `market.store.ts`, `observability.store.ts`). Zero `auth.store.ts` exists.
- **API & Streaming Clients (`frontend/src/services/`)**:
  - `api/client.ts`: `fetch` wrapper reading `localStorage` bearer token if manually populated, unwrapping `{data, meta}` or returning raw JSON, lacking HTTP retry/backoff or 401 redirect.
  - `api/{observability,market,analytics,catalog,agent}.service.ts`: Domain HTTP clients with client-side field normalizers (`normalizeOverviewPayload`, `mapRawTrace`) compensating for backend response drift.
  - `api/sse.ts`: Native `EventSource` client wrapping `/api/v1/observability/stream` (`snapshot`, `trace`, `heartbeat` events) and agent run SSE.
  - `websocket/ws-client.ts`: Reconnecting WebSocket client targeting `/ws/v1/observability/stream` (`ping` -> `pong`, heartbeat interval).
  - `auth/auth.service.ts`: Reads `localStorage['fmdp_user_profile']` or defaults to `{ username: 'quant_admin', role: 'admin' }`.

## 3. Verified `AS-IS` Frontend Gaps & Technical Debt

| Area | Observed Defect / Mismatch | Code Location |
|---|---|---|
| **Auth / RBAC Bypass UX** | Unauthenticated session defaults to `ADMIN`; no login screen, token refresh, or route guard exists. | `frontend/src/services/auth/auth.service.ts` |
| **Non-Wired Shell Controls** | `LIVE/DEMO` toggle never propagates to modules; `appStore.addNotification` queue is never rendered in DOM; sidebar collapse button is missing. | `frontend/src/app/layouts/MainLayout.ts` |
| **Hardcoded / Mock Fallbacks** | `DashboardModule` hardcodes `5/5 Connected` core store text; `PipelineDag.ts` has static SVG metrics; `CatalogService.getLineage()` falls back to static 8-node mock; `AgentService.getRuns()` falls back to hardcoded node durations. | `DashboardModule.ts`, `PipelineDag.ts`, `catalog.service.ts`, `agent.service.ts` |
| **Broken / Missing API Calls** | `auth.service.getApiKeys()` calls nonexistent `GET /api/v1/auth/api-keys` (405 -> `[]`); `revokeApiKey()` calls nonexistent `DELETE /api/v1/auth/api-keys/{id}`; `AdministrationModule` discards `api_key_once` secret; `setStreamControl()` targets missing endpoint. | `auth.service.ts`, `AdministrationModule.ts`, `observability.service.ts` |
| **Buggy / Unused Modules** | `MarketAnalyticsModule` uses `|| 0.45` / `|| 0.012` / `|| 1440` masking valid `0` metrics and leaks `window.resize` listeners; `StateView.ts` is unused; `frontend/tests/` import zero source files from `src/`. | `MarketAnalyticsModule.ts`, `StateView.ts`, `frontend/tests/` |
| **Stale `frontend/README.md`** | Docs cite nonexistent `public/icons/`, `src/app/providers/`, and `src/hooks/`. | `frontend/README.md` |
