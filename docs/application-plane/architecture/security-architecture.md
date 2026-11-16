---
doc_id: APP-ARCH-SEC-001
title: "Application Plane Security Architecture & Control Gaps"
doc_type: architecture
plane: application-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/presentation/router.py"
    - "src/serving/api/modules/iam/domain/ports.py"
    - "src/serving/api/modules/iam/domain/security.py"
    - "src/shared/config/settings.py"
related_docs:
  - APP-ARCH-ROOT-001
  - ADR-APP-0002
  - CAP-APP-IAM-TM-001
  - CAP-APP-OPS-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Cataloged implemented edge defenses vs unauthenticated business endpoints, JWT key defaults, and frontend admin-default exposure."
---

# Application Plane Security Architecture & Control Gaps

> [!WARNING]
> **Status `DRAFT` — Blocked on Security Remediation**: Several `CRITICAL` security controls (`AUTHZ` dependencies, DB user verification, JWT secret enforcement, admin UI auth) are `NOT_IMPLEMENTED`.

## 1. Scope & Context: Implemented Edge Controls vs Unprotected Routes (`AS-IS`)

| Security Layer | Implemented (`AS-IS`) | Verified Gap / Vulnerability | Severity |
|---|---|---|---|
| **HTTP Edge Defense** | `install_security_defense_middleware` validates Host header, checks path/query regex WAF (`SQLi`/`XSS`/path traversal), enforces sliding-window IP rate limits, and injects HSTS, CSP, `X-Frame-Options: DENY`. | HTTP request JSON bodies are NOT WAF-inspected; `X-Forwarded-For` is trusted from any peer; microservice ports `8001..8004, 8006, 8007` lack this middleware. | `HIGH` |
| **Authentication** | `POST /api/v1/auth/token` hashes/verifies passwords using PBKDF2-HMAC-SHA256 (210k iterations) and signs HS256 JWTs bound to client IP HMAC. | **Zero user lookup (`SEC-AUDIT-001`)**: `POST /auth/token` hashes the supplied password and immediately verifies against that same hash, trusting caller-supplied `role`. `settings.py:34` defaults `jwt_secret_key` to a hardcoded literal if env is unset. | `CRITICAL` |
| **Authorization (RBAC)** | `ROLE_CAPABILITIES` defines scopes for `VIEWER`, `ANALYST`, `OPERATOR`, `ADMIN`. | **Zero route enforcement (`SEC-AUDIT-003`)**: Zero FastAPI endpoints use `Depends` auth checks; unauthenticated callers can run `/auth/revoke`, `/auth/api-keys`, `/evict/{symbol}`, `/catalog/instruments/{symbol}`, `/agents/runs`, `/demo/emit`, `/microservices/dispatch/{id}`. Also `UserRole.SERVICE` is missing from `ROLE_CAPABILITIES`. | `CRITICAL` |
| **Frontend Auth** | `auth.service.ts` checks `localStorage['fmdp_user_profile']`. | Defaults unauthenticated visitors to `quant_admin` (`role: admin`) with full access to Administration, Data Flow, and Agent panels. | `CRITICAL` |
| **Health Endpoint Info** | `/api/v1/health/ready` returns `redacted` masked dependency addresses. | Unauthenticated and returns static `"ready"` without executing real health probes. | `LOW` |

## 2. Building Blocks & Target Security Remediation (`ADR-APP-0002`)

1. Enforce mandatory `Depends(require_capability(...))` across all mutating, admin, agent, and private read routes.
2. Back `/auth/token`, `/auth/revoke`, and `/auth/api-keys` with persistent Postgres tables (`users`, `api_keys`, `revoked_tokens`) and fail fast if `JWT_SECRET_KEY` is default outside local tests.
3. Add explicit login UI and RBAC route guards in `frontend/src/app/router/` removing the `quant_admin` default.
4. Restrict `X-Forwarded-For` parsing to explicit trusted proxy CIDRs and remove standalone microservice port exposure outside private service mesh.
