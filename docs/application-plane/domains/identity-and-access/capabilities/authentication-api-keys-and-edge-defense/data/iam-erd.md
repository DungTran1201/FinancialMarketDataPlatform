---
doc_id: DIAG-APP-IAM-ERD-001
title: "ERD Diagram: IAM Users, Agent Ownership & Target API Keys"
doc_type: diagram
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
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/identity-and-access/capabilities/authentication-api-keys-and-edge-defense/data/database-design.md"
related_docs:
  - CAP-APP-IAM-DB-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Rendered Postgres users and target api_keys/revocations ERD."
---

# ERD Diagram: IAM Users, Agent Ownership & Target API Keys

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-IAM-ERD-001` |
| **Title & Purpose** | Postgres `users` (Unused `AS-IS` DDL) & Target `api_keys` / `agent_runs` FK Links |
| **Owner Role & Scope** | `database-architect / CAP-APP-IAM-001` |
| **Authoritative Source** | [database-design.md](database-design.md) (`CAP-APP-IAM-DB-001`) |
| **Notation** | `Mermaid erDiagram` (`Crow's Foot`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
erDiagram
    users {
        uuid id PK
        text email UK
        text password_hash
        text role
        boolean is_active
        timestamptz created_at
    }
    api_keys_target {
        uuid key_id PK
        uuid owner_user_id FK
        text key_prefix
        text key_sha256_hash UK
        text role
        timestamptz revoked_at
    }
    agent_runs {
        uuid run_id PK
        uuid requested_by FK
        text symbol
        text status
    }

    users ||--o{ api_keys_target : "TARGET (NOT IN DDL)"
    users ||--o{ agent_runs : "requested_by FK (UNWIRED)"
```

## 3. Legend

- **`users` & `agent_runs`**: Declared in `deploy/postgres/init/01_schema.sql` with zero runtime SQL queries `AS-IS`.
- **`api_keys_target`**: Missing table required to reconcile `POST/GET/DELETE /api/v1/auth/api-keys`.
