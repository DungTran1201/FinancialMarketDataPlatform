---
doc_id: CAP-APP-IAM-TM-001
title: "Threat Model: Authentication, API Keys & Edge Defense"
doc_type: specification
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
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
    - "src/shared/config/settings.py"
    - "frontend/src/services/auth/auth.service.ts"
related_docs:
  - CAP-APP-IAM-SEC-001
  - DIAG-APP-IAM-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Analyzed critical auth bypass, caller role forging, default JWT key, XFF spoofing, and SPA quant_admin fallback."
---

# Threat Model: Authentication, API Keys & Edge Defense

Derived diagram: [threat-model-diagram.md](threat-model-diagram.md) (`DIAG-APP-IAM-TM-001`).

## 1. Assets, Entry Points & Trust Boundaries

- **Assets**: Signing secret (`jwt_secret_key`), admin/operator JWTs, `fmdp_live_*` API keys, Postgres `users`, client IP privacy hashes, and downstream mutating endpoints (`/market/ingest`, `/catalog`, `/agents`, `/auth`).
- **Entry Points**: Public FastAPI endpoints `/api/v1/auth/*`, downstream API routers on `:8000` and `:8001..:8007`, HTTP headers (`Host`, `X-Forwarded-For`), and browser `localStorage` in `frontend/`.
- **Trust Boundaries**: Untrusted Internet/LAN Client <-> Edge Defense Middleware (`main.py`/`services/iam.py`) <-> Router Handlers <-> Ephemeral Memory / Postgres `01_schema.sql`.

## 2. Threat Scenarios, `AS-IS` Gaps & Mitigations

| Threat ID | Threat Scenario | Severity | `AS-IS` Mitigations & Verified Gaps | Residual Risk |
|---|---|---|---|---|
| `THR-IAM-001` | **Privilege Escalation on Login (`SEC-AUDIT-001`)**: Attacker sends `POST /api/v1/auth/token` with arbitrary `username`, random 8-char `password`, and `"role": "admin"` and receives a valid signed ADMIN JWT. | `CRITICAL` | Self-hash check verifies input password against itself; zero Postgres `users` check! | `CRITICAL` (`BLOCKED`) |
| `THR-IAM-002` | **Unauthenticated Route Access (`SEC-AUDIT-003`)**: Caller omits `Authorization` header completely and calls `/auth/revoke`, `/auth/api-keys`, `/catalog/*`, `/agents/runs`, `/demo/emit`, or ports `8001..8007`. | `CRITICAL` | Zero `Depends` auth guards across ALL business & admin routers! | `CRITICAL` (`BLOCKED`) |
| `THR-IAM-003` | **Hardcoded Default JWT Secret**: Env var `JWT_SECRET_KEY` unset -> attacker forges HS256 JWTs offline using default literal in `settings.py:34`. | `CRITICAL` | Startup permits default secret unconditionally. | `CRITICAL` (`BLOCKED`) |
| `THR-IAM-004` | **X-Forwarded-For Spoofing**: Attacker sets arbitrary `X-Forwarded-For` header to bypass IP-bound JWT check or DoS another IP's rate-limit bucket. | `HIGH` | `_extract_client_ip` blindly trusts `X-Forwarded-For` without trusted proxy CIDR allowlist. | `HIGH` (`OPEN`) |
| `THR-IAM-005` | **Frontend Default Admin Session**: Anonymous user opens SPA -> `auth.service.ts` defaults UI identity to `quant_admin` (`admin`). | `HIGH` | Zero login screen or UI RBAC enforcement (`ADR-APP-0002`). | `HIGH` (`BLOCKED`) |
