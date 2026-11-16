---
doc_id: APP-QA-PLAN-001
title: "Application Plane Test Plan"
doc_type: specification
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: qa-lead
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/unit/test_security_and_defense.py"
    - "tests/integration/test_three_planes_framework.py"
    - "tests/integration/test_realtime_observability_dashboard.py"
    - "tests/architecture/test_clean_architecture_boundaries.py"
related_docs:
  - APP-ROOT-001
  - APP-ARCH-COMPAT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Consolidated verified ASGI integration tests and frontend/security verification gaps across Application Plane capabilities."
---

# Application Plane Test Plan

## 1. Automated Verification Suites (`AS-IS`)

- **Security & API Defense Tests (`tests/unit/test_security_and_defense.py`)**: Exercises PBKDF2/SHA-256 hashing, IP HMAC encryption, `POST /auth/token`, `/verify`, `/revoke`, `/api-keys`, WAF path/query regex rejection (`403`), Host header blocking (`400`), and sliding-window rate limiting (`429`).
- **Three-Plane API & Gateway Tests (`tests/integration/test_three_planes_framework.py`)**: Exercises `/market`, `/historical`, `/analytics`, `/catalog`, `/agents/runs`, `/reports`, `/microservices/{topology,health,dispatch}`, and `data-platform/v01` endpoints in-process.
- **Observability API, SSE & WS Tests (`tests/integration/test_realtime_observability_dashboard.py`)**: Exercises `/observability/{overview,topology,kafka,storage,latency,traces,candles,live/probe,demo/emit,stream}` and WebSocket telemetry.
- **Clean Architecture Boundary Check (`tests/architecture/test_clean_architecture_boundaries.py`)**: Enforces `TC-006` verifying presentation routers do not directly import lower data-plane storage adapters.

## 2. Explicit Coverage Gaps (`AS-IS`)

- **Missing RBAC Negative Tests on Business Routes**: Because no routes use `Depends` RBAC checks today, unauthorized access tests (`401`/`403` missing/insufficient Bearer token on mutating endpoints) are `NOT_IMPLEMENTED`.
- **Frontend E2E & Vite Build Verification**: `frontend/tests/` import zero TypeScript modules from `frontend/src/`, and `node`/`npm`/`tsc` are absent from the local sandbox PATH, leaving TypeScript compilation (`npx tsc --noEmit`) and real DOM interaction flows unverified here.
- **Postgres Control-Plane Persistence**: Zero integration tests hit real PostgreSQL tables in `01_schema.sql` (`NOT_IMPLEMENTED`).
