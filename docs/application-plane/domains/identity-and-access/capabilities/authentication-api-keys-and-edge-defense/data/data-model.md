---
doc_id: CAP-APP-IAM-DM-001
title: "Logical Data Model: Users, Sessions & API Keys"
doc_type: specification
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: NOT_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "deploy/postgres/init/01_schema.sql"
    - "src/serving/api/modules/iam/domain/security.py"
related_docs:
  - CAP-APP-IAM-DB-001
  - DIAG-APP-IAM-ERD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Defined logical entity attributes for users, JWT revocation records, and missing api_keys model."
---

# Logical Data Model: Users, Sessions & API Keys

## 1. Logical Entities

- **`UserPrincipal`** (`users` in `01_schema.sql`, **unwired `AS-IS`**): Identity identified by UUID `id` and unique `email` (or `username` mapping needed — note `POST /auth/token` takes `username` while `01_schema.sql` uses `email`!), `password_hash`, `role` (`viewer|analyst|operator|admin|service`), `is_active`, `created_at`.
- **`RevokedTokenRecord`** (`AS-IS` in-memory `_revoked_token_hashes: set[str]`): SHA-256 digest of revoked JWT strings; requires persistent shared store with TTL matching `exp`.
- **`ApiKeyRecord`** (`AS-IS` discarded dataclass in `security.py`): `key_id`, `key_prefix`, `key_sha256_hash`, `role`. Zero SQL table exists in `01_schema.sql` (`OPEN-IAM-001`).

## 2. Schema Drift & Open Modeling Questions

- `POST /api/v1/auth/token` accepts `username` (`>= 3` chars), whereas `deploy/postgres/init/01_schema.sql` defines `users(email UNIQUE)` with no `username` column. Reconciliation is required (`OPEN`).
- `api_keys` persistence and audit timestamps (`created_by`, `last_used_at`, `revoked_at`) are absent from `01_schema.sql`.
