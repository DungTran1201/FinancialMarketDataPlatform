---
doc_id: ADR-APP-0002
title: "ADR-APP-0002: Target Application Auth, DB Persistence & SPA Route Guard Remediation"
doc_type: adr
plane: application-plane
scope_level: plane
status: DRAFT
implementation_status: NOT_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/presentation/router.py"
    - "deploy/postgres/init/01_schema.sql"
    - "frontend/src/services/auth/auth.service.ts"
related_docs:
  - APP-ADR-ROOT-001
  - APP-ARCH-SEC-001
  - CAP-APP-IAM-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Captured TARGET security remediation plan for unauthenticated routers, transient credential hashing, and frontend admin default."
---

# ADR-APP-0002: Target Application Auth, DB Persistence & SPA Route Guard Remediation

## 1. Context & Problem (`AS-IS` Blockers)

`AS-IS` code leaves every business router unauthenticated, accepts client-supplied `role` claims in `POST /auth/token` without Postgres verification (`SEC-AUDIT-001`), fails to persist generated API keys or revoked token hashes, misses `UserRole.SERVICE` in `ROLE_CAPABILITIES`, and defaults unauthenticated browser visitors to `quant_admin`.

## 2. Considered Options

1. **Option 1 (Rejected)**: Edge-only IP rate limiting + frontend UI role checks with zero FastAPI route guards.
2. **Option 2 (Chosen Target)**: Full route-level `Depends(require_capability(...))`, Postgres `users` + `api_keys` persistence, and explicit SPA login UI.

## 3. Target Decision (`PROPOSED` Pending Implementation & Security Sign-Off)

1. Wire `Depends(require_capability("..."))` and Bearer JWT / API-key verification onto all domain/gateway endpoints (except explicit `GET /api/v1/health/live` & `POST /api/v1/auth/token`).
2. Persist `users` (`01_schema.sql`), an `api_keys` table (not yet in DDL -> `OPEN`), and token revocations in PostgreSQL/Redis rather than ephemeral process dicts.
3. Add `UserRole.SERVICE` scopes to `ROLE_CAPABILITIES` and enforce non-default `JWT_SECRET_KEY` outside local unit test harnesses.
4. Remove the `quant_admin` fallback in `auth.service.ts`, add a SPA login workflow, and enforce client-side route guards backed by server-side RBAC.

## 4. Expected Consequences

- Breaks anonymous automated smoke scripts that omit credentials unless updated with valid test tokens; closes `SEC-AUDIT-001` & `SEC-AUDIT-003`.
