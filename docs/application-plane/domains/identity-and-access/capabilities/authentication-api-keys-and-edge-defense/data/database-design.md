---
doc_id: CAP-APP-IAM-DB-001
title: "Physical Database Design: Postgres `users` & Target `api_keys`"
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
related_docs:
  - CAP-APP-IAM-DM-001
  - DIAG-APP-IAM-ERD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Documented PostgreSQL 16 users DDL and missing api_keys/revoked_tokens physical schema requirements."
---

# Physical Database Design: Postgres `users` & Target `api_keys`

## 1. Existing Unused Postgres DDL (`deploy/postgres/init/01_schema.sql`)

| Column | Type & Constraints | Purpose |
|---|---|---|
| `id` | `UUID PRIMARY KEY DEFAULT gen_random_uuid()` | Principal identifier referenced by `agent_runs.requested_by` |
| `email` | `TEXT NOT NULL UNIQUE` | Login lookup key (**Drift**: `/auth/token` passes `username`) |
| `password_hash` | `TEXT NOT NULL` | Salted `PBKDF2-HMAC-SHA256` hash (`$pbkdf2$...`) |
| `role` | `TEXT NOT NULL CHECK (role IN ('viewer', 'analyst', 'operator', 'admin', 'service'))` | Authoritative server-side RBAC role |
| `is_active` | `BOOLEAN NOT NULL DEFAULT TRUE` | Account disable switch |
| `created_at` | `TIMESTAMPTZ NOT NULL DEFAULT NOW()` | Audit timestamp |

## 2. Missing Target Tables & Migration / Rollback Policy

- **`api_keys` (`NOT_IMPLEMENTED`, `OPEN-IAM-001`)**: Required for `POST/GET/DELETE /api/v1/auth/api-keys` storing `key_id`, `key_prefix`, `key_sha256_hash` (UNIQUE index), `role`, `owner_user_id` FK -> `users(id)`, `revoked_at`.
- **`jwt_revocations` or Redis `revoked:jti:<hash>` (`NOT_IMPLEMENTED`)**: Required so `POST /auth/revoke` survives container restarts.
- **Migration Status**: Currently zero Alembic/Flyway migration runner exists beyond Compose container init script `01_schema.sql`.
