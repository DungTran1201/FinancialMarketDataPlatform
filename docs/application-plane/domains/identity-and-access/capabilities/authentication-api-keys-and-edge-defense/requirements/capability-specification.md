---
doc_id: CAP-APP-IAM-REQ-001
title: "Capability Specification: Authentication, API Keys & Edge Defense"
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
    - "src/serving/api/modules/iam/domain/ports.py"
    - "src/serving/api/modules/iam/domain/security.py"
related_docs:
  - CAP-APP-IAM-DOC-001
  - CAP-APP-IAM-RULE-001
  - CAP-APP-IAM-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Authored atomic FRs and AS-IS implementation gaps for IAM & Edge Defense."
---

# Capability Specification: Authentication, API Keys & Edge Defense

## 1. Capability Scope & `AS-IS` Reality

Implements the FastAPI HTTP edge defense middleware (`install_security_defense_middleware`) and `/api/v1/auth` routes alongside domain RBAC roles (`UserRole`), PBKDF2 hashing, and HS256 JWT generation. **Gaps**: no persistent user verification, unauthenticated token revocation and API key minting, no `GET`/`DELETE` API key routes, and no RBAC dependency injected into business routes.

## 2. Functional Requirements

| Req ID | Requirement Statement | `AS-IS` Evidence | Target / Gap |
|---|---|---|---|
| `FR-IAM-001` | System MUST authenticate users against stored salted PBKDF2 credentials (`users` table) and issue HS256 JWT bound to client IP HMAC (`bound_ip_hash`). | `iam/presentation/router.py:183-226` | **CRITICAL GAP (`SEC-AUDIT-001`)**: Hashes transient password & honors caller-supplied `role` with zero Postgres lookup. |
| `FR-IAM-002` | System MUST verify HS256 JWT signatures, expiry, revocation status, and IP binding on `POST /auth/verify` and on every protected endpoint via FastAPI `Depends`. | `/verify` works at `L228-251` | **CRITICAL GAP (`SEC-AUDIT-003`)**: Zero business endpoints enforce `Depends` RBAC checks; revocation set is in-memory only. |
| `FR-IAM-003` | Authenticated admins MUST mint (`POST`), list (`GET`), and revoke (`DELETE`) SHA-256 hashed scoped API keys (`fmdp_live_*`) persisted across restarts. | `POST /auth/api-keys` at `L264-281` returns `api_key_once` | **GAP (`COMPAT-001/002`)**: Endpoint is unauthenticated, discards key without DB persistence, and lacks `GET`/`DELETE` routes. |
| `FR-IAM-004` | Edge middleware MUST block untrusted `Host` headers (`400`), regex-detected URL path/query WAF threats (`403`), and sliding-window rate-limit overflows (`429`). | `iam/presentation/router.py:59-161` | Missing on standalone ports `8001..8004, 8006, 8007`; JSON body not inspected; `X-Forwarded-For` unvalidated. |
| `FR-IAM-005` | System MUST expose HTTPS public origin topology and HMAC-masked internal host bindings (`GET /api/v1/auth/domains`) without plaintext infrastructure IPs/passwords. | `iam/presentation/router.py:283-307` | Endpoint currently unauthenticated (`RBAC` needed for ops visibility). |
