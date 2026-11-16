---
doc_id: APP-ARCH-ROOT-001
title: "Application Plane Architecture Hub"
doc_type: index
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
    - "frontend/src/main.ts"
related_docs:
  - APP-ROOT-001
  - APP-ARCH-001
  - APP-ARCH-FE-001
  - APP-ARCH-BE-001
  - APP-ARCH-DATA-001
  - APP-ARCH-API-001
  - APP-ARCH-SEC-001
  - APP-ARCH-DEP-001
  - APP-ARCH-COMPAT-001
  - APP-ADR-ROOT-001
  - DIAG-APP-C4-001
  - DIAG-APP-COMP-001
  - DIAG-APP-DEP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Indexed all Application Plane architectural viewpoints, ADRs, compatibility matrix, and diagrams."
---

# Application Plane Architecture Hub

## 1. Architecture Viewpoints

- [application-architecture.md](application-architecture.md) (`APP-ARCH-001`) — Holistic Application Plane boundaries and dual monolith/microservices deployment behavior.
- [frontend-architecture.md](frontend-architecture.md) (`APP-ARCH-FE-001`) — Vanilla TypeScript Vite SPA, hash router, state stores, SSE/WS clients, and UI discrepancies.
- [backend-architecture.md](backend-architecture.md) (`APP-ARCH-BE-001`) — FastAPI router tree, microservice registry, `PlatformRuntimeContainer`, and Clean Architecture boundary checks (`TC-006`).
- [application-data-architecture.md](application-data-architecture.md) (`APP-ARCH-DATA-001`) — In-memory `AS-IS` dicts vs `TARGET` Postgres tables in `deploy/postgres/init/01_schema.sql`.
- [api-and-integration-architecture.md](api-and-integration-architecture.md) (`APP-ARCH-API-001`) — REST/SSE/WS endpoints, Vite proxy, and payload envelope taxonomy.
- [security-architecture.md](security-architecture.md) (`APP-ARCH-SEC-001`) — Security defense middleware, RBAC gaps, and frontend admin-default exposure.
- [deployment-architecture.md](deployment-architecture.md) (`APP-ARCH-DEP-001`) — Single-process Compose runtime vs `--profile microservices` vs static frontend bundling.
- [screen-and-api-compatibility-matrix.md](screen-and-api-compatibility-matrix.md) (`APP-ARCH-COMPAT-001`) — Exhaustive UI screen-to-backend route compatibility mapping.

## 2. Decisions & Diagrams

- [decisions/README.md](decisions/README.md) (`APP-ADR-ROOT-001`) — Application Plane ADRs (`ADR-APP-0001`, `ADR-APP-0002`).
- [diagrams/application-c4-container.md](diagrams/application-c4-container.md) (`DIAG-APP-C4-001`)
- [diagrams/frontend-backend-components.md](diagrams/frontend-backend-components.md) (`DIAG-APP-COMP-001`)
- [diagrams/deployment-topology.md](diagrams/deployment-topology.md) (`DIAG-APP-DEP-001`)
