---
doc_id: APP-DOM-IAM-SPEC-001
title: "Domain Specification: Identity, Access & Edge Security"
doc_type: specification
plane: application-plane
scope_level: domain
domain: identity-and-access
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
    - "src/shared/security/primitives.py"
    - "deploy/postgres/init/01_schema.sql"
related_docs:
  - APP-DOM-IAM-001
  - APP-ARCH-SEC-001
  - ADR-APP-0002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Defined IAM domain boundaries, AS-IS security gaps, and target DB/middleware enforcement requirements."
---

# Domain Specification: Identity, Access & Edge Security

## 1. Domain Scope & Reality (`AS-IS`)

1. **HTTP Defense Middleware**: Checks `Host` allowlist (`UNTRUSTED_HOST_HEADER`), path/query regex WAF (`WAF_THREAT_DETECTED`), sliding-window IP rate limits (`RATE_LIMIT_EXCEEDED`), and injects HSTS/CSP/frame/IP-token headers (`main.py` and `services/iam.py` only).
2. **JWT & API Key Operations**: Issues/verifies/revokes HS256 JWTs bound to client IP HMAC (`JwtSecurityService`) and generates `fmdp_live_*` keys (`CredentialHasher`).
3. **Blocking Gaps (`SEC-AUDIT-001..005`)**: Zero DB credential lookup (`POST /auth/token` self-verifies supplied password and honors caller-supplied `role`), zero route `Depends` RBAC enforcement, missing `UserRole.SERVICE` capability entry, unpersisted API keys and revocations, missing `GET`/`DELETE /auth/api-keys` routes expected by frontend, and hardcoded `jwt_secret_key` default.

## 2. Target Domain Contracts & Remediation Ownership

This domain owns remediation per [ADR-APP-0002](../../architecture/decisions/adr-0002-application-auth-remediation-target.md): Postgres `users` verification, an explicit `api_keys` storage contract, unified route-level RBAC `Depends`, and frontend login session state.
