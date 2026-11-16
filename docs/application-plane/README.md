---
doc_id: APP-ROOT-001
title: "Application Plane — Serving APIs, SPA & Business Controls"
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
  - OVR-ROOT-001
  - APP-ARCH-ROOT-001
  - APP-ARCH-COMPAT-001
  - APP-QA-PLAN-001
  - CAP-APP-IAM-DOC-001
  - CAP-APP-MKT-DOC-001
  - CAP-APP-CAT-DOC-001
  - CAP-APP-OPS-DOC-001
  - CAP-APP-AGT-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Created Application Plane documentation root covering backend serving APIs, TypeScript SPA, domains, capabilities, contracts, and security gaps."
---

# Application Plane — Serving APIs, SPA & Business Controls

**Scope**: User-facing web application (`frontend/` TypeScript SPA), unified FastAPI API Gateway (`src/serving/api/main.py`), microservice decomposition routers (`src/serving/api/services/`), IAM/security middleware (`src/serving/api/modules/iam/`), Data Catalog, Observability control endpoints, and Agent run/report serving facades.

> [!CAUTION]
> **Critical Security & State Reality (`AS-IS`)**: While [router.py](../../src/serving/api/modules/iam/presentation/router.py) implements PBKDF2 hashing, HMAC IP binding, HS256 JWT issuance/verification, WAF inspection, and sliding-window rate limiting, **zero business endpoints inject FastAPI `Depends` JWT/RBAC checks**. Furthermore, Postgres tables in [01_schema.sql](../../deploy/postgres/init/01_schema.sql) have zero runtime DB driver queries—all Application Plane state currently lives in memory inside `PlatformRuntimeContainer`.

## 1. Architecture, Compatibility & Operations

- [architecture/README.md](architecture/README.md) (`APP-ARCH-ROOT-001`) — Plane architecture hub, ADRs, and diagrams.
- [architecture/screen-and-api-compatibility-matrix.md](architecture/screen-and-api-compatibility-matrix.md) (`APP-ARCH-COMPAT-001`) — Frontend screen-to-endpoint contract parity and mismatch register.
- [shared-contracts/error-catalog.md](shared-contracts/error-catalog.md) (`APP-ERR-SHARED-001`) — Plane-wide HTTP error shapes (`error.code`, HTTP `detail`, middleware blocks).
- [operations/runbook.md](operations/runbook.md), [incident-and-recovery.md](operations/incident-and-recovery.md), [observability-and-slo.md](operations/observability-and-slo.md), [test-plan.md](operations/test-plan.md).

## 2. Domains & Capabilities

| Domain | Capability ID | Capability | Risk Tier | `AS-IS` Status |
|---|---|---|---|---|
| [identity-and-access](domains/identity-and-access/README.md) | `CAP-APP-IAM-001` | [Authentication, API Keys & Edge Defense](domains/identity-and-access/capabilities/authentication-api-keys-and-edge-defense/README.md) | `HIGH_CRITICAL` | `PARTIALLY_IMPLEMENTED` |
| [market-experience-and-catalog](domains/market-experience-and-catalog/README.md) | `CAP-APP-MKT-001` | [Market & Analytics Query Portal](domains/market-experience-and-catalog/capabilities/market-and-analytics-query-portal/README.md) | `MEDIUM` | `PARTIALLY_IMPLEMENTED` |
| [market-experience-and-catalog](domains/market-experience-and-catalog/README.md) | `CAP-APP-CAT-001` | [Instrument & Data Catalog](domains/market-experience-and-catalog/capabilities/instrument-and-data-catalog/README.md) | `MEDIUM` | `PARTIALLY_IMPLEMENTED` |
| [platform-operations-and-control](domains/platform-operations-and-control/README.md) | `CAP-APP-OPS-001` | [Observability, Control & Gateway](domains/platform-operations-and-control/capabilities/observability-control-and-gateway/README.md) | `HIGH_CRITICAL` | `PARTIALLY_IMPLEMENTED` |
| [agent-experience-and-reporting](domains/agent-experience-and-reporting/README.md) | `CAP-APP-AGT-001` | [Agent Run & Report Portal](domains/agent-experience-and-reporting/capabilities/agent-run-and-report-portal/README.md) | `MEDIUM` | `PARTIALLY_IMPLEMENTED` |
