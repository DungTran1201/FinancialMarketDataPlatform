---
doc_id: APP-ADR-ROOT-001
title: "Application Plane Architecture Decision Records"
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
    - "frontend/vite.config.ts"
related_docs:
  - APP-ARCH-ROOT-001
  - ADR-APP-0001
  - ADR-APP-0002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Indexed Application Plane ADRs."
---

# Application Plane Architecture Decision Records

## 1. Decision Register

| ADR ID | Decision | Status | Implementation Status |
|---|---|---|---|
| [ADR-APP-0001](adr-0001-frontend-proxy-and-spa-state.md) | Same-Origin Vite/Nginx Reverse Proxy & Vanilla TS Hash SPA Stores | `IN_REVIEW` | `PARTIALLY_IMPLEMENTED` |
| [ADR-APP-0002](adr-0002-application-auth-remediation-target.md) | Target FastAPI Dependency RBAC, Postgres User/API-Key Persistence & SPA Login Guard | `DRAFT` (Blocked on implementation sign-off) | `NOT_IMPLEMENTED` |
