---
doc_id: CAP-APP-IAM-TS-001
title: "Test Scenarios: IAM & Edge Defense"
doc_type: specification
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: qa-lead
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/unit/test_security_and_defense.py"
related_docs:
  - CAP-APP-IAM-DOC-001
  - CAP-APP-IAM-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Documented passing edge-defense tests alongside missing target RBAC/Postgres negative security tests."
---

# Test Scenarios: IAM & Edge Defense

## 1. Covered `AS-IS` Test Scenarios (`test_security_and_defense.py`)

- **`TS-IAM-001`**: Valid `POST /auth/token` issues IP-bound HS256 JWT; `POST /auth/verify` succeeds from matching IP and rejects (`401`) from altered IP or after `POST /auth/revoke`.
- **`TS-IAM-002`**: `install_security_defense_middleware` blocks untrusted `Host` (`400`), SQLi/XSS URL query threats (`403`), and burst rates (`429` with `Retry-After` and `X-Client-IP-Token`).
- **`TS-IAM-003`**: `POST /auth/api-keys` generates `fmdp_live_*` key metadata and `GET /auth/domains` returns HTTPS origins + masked container addresses.

## 2. Unimplemented Target Negative Tests (`BLOCKED`)

- **`TS-IAM-004` (`NOT_IMPLEMENTED`)**: Reject `POST /auth/token` with `role=admin` when Postgres `users.role=viewer` (`SEC-IAM-001`).
- **`TS-IAM-005` (`NOT_IMPLEMENTED`)**: Reject unauthenticated `POST /auth/revoke` & `POST /auth/api-keys` (`401`/`403`, `SEC-IAM-002`).
