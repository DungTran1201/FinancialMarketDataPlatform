---
doc_id: CAP-APP-IAM-UC-001
title: "Use Case UC-IAM-001: Issue & Verify IP-Bound JWT Token"
doc_type: specification
plane: application-plane
scope_level: use-case
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/presentation/router.py"
    - "src/serving/api/modules/iam/domain/security.py"
related_docs:
  - CAP-APP-IAM-REQ-001
  - DIAG-APP-IAM-SEQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented UC-IAM-001 flow, preconditions, validation exceptions, and self-hash credential vulnerability."
---

# Use Case UC-IAM-001: Issue & Verify IP-Bound JWT Token

## 1. Use Case Header & Actors

- **Primary Actor**: Platform User / Automated Service calling `POST /api/v1/auth/token` and `POST /api/v1/auth/verify`.
- **Preconditions**: Request passes edge `defense_in_depth_middleware` (`Host` allowlist, WAF regex check, `AUTH` tier limit <= 10 req/min per client IP hash).
- **Postconditions (`AS-IS`)**: Signed HS256 JWT returned with `jti`, `token_sha256_hash`, and `bound_ip_hash`. **Target**: Credentials verified against `users` table (`01_schema.sql`).

## 2. Main Flow & Alternative / Exception Flows

1. Caller submits `POST /api/v1/auth/token` with JSON `{ username, password, role }`.
2. Middleware resolves client IP (`X-Forwarded-For` -> `X-Real-IP` -> socket host) and enforces `AUTH` rate-limit tier.
3. Router checks `len(username) >= 3` and `len(password) >= 8` and parses `UserRole(role)` (`HTTP 422` on failure).
4. **AS-IS Anomaly**: Router hashes submitted `password` via `CredentialHasher.hash_password(password)` and immediately verifies it against itself (`L202-204`) without checking `users` in PostgreSQL!
5. `JwtSecurityService.issue_token(...)` generates HS256 JWT bound to `ip_cipher.hash_ip(client_ip)` and TTL `cfg.jwt_access_token_expire_minutes * 60`.
6. Caller verifies token via `POST /api/v1/auth/verify` (`{ access_token }`); `verify_token` checks signature, expiry, in-memory revocation set, and `ip_hash` equality, returning `HTTP 401` on `SecurityViolationError`.
- **Exception E1 (`429 RATE_LIMIT_EXCEEDED`)**: Triggered after 10 requests/min from same IP hash; returns `Retry-After` header.
- **Exception E2 (`401` IP Mismatch)**: Client IP changes between `/token` and `/verify` -> `"Token IP mismatch"` / `SecurityViolationError`.
