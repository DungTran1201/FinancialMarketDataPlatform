---
doc_id: ADR-APP-0001
title: "ADR-APP-0001: Same-Origin Vite/Nginx Reverse Proxy & Vanilla TS Hash SPA"
doc_type: adr
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "frontend/vite.config.ts"
    - "deploy/nginx/nginx.conf"
    - "frontend/src/app/router/router.ts"
related_docs:
  - APP-ADR-ROOT-001
  - APP-ARCH-FE-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Recorded decision to use zero-dependency TypeScript hash SPA behind same-origin /api and /ws proxy."
---

# ADR-APP-0001: Same-Origin Vite/Nginx Reverse Proxy & Vanilla TS Hash SPA

## 1. Context & Problem

The Application Plane requires an operator console supporting REST queries, SSE telemetry streams, and bidirectional WebSockets without requiring CORS preflight complexity or heavy third-party frontend frameworks during rapid platform prototyping.

## 2. Considered Options

1. **Option 1 (Chosen)**: Zero-dependency TypeScript hash SPA behind same-origin Vite (`frontend/vite.config.ts`) and Nginx (`deploy/nginx/nginx.conf`) proxies.
2. **Option 2 (Deferred)**: External SPA framework (`React`/`Next`) with cross-origin CORS credentials.

## 3. Decision & Consequences

- Use a zero-framework vanilla TypeScript ES2022 hash-routed SPA (`#/dashboard`, `#/data-flow`, etc.) built by Vite into Nginx static assets, proxying `/api` and `/ws` over same-origin paths (`frontend/vite.config.ts`, `frontend/nginx.conf`).
- **Positive**: Zero CORS headers required on `serving-api`; lightweight bundle (`dist/`).
- **Consequences (`AS-IS`)**: Hash routes bypass clean path URLs; custom DOM cleanup discipline is needed (evidenced by leaked `window.resize` listeners in `MarketAnalyticsModule.ts`).
