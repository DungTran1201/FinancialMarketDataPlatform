---
doc_id: APP-ARCH-DATA-001
title: "Application Data Architecture (`AS-IS` Memory vs `TARGET` Postgres)"
doc_type: architecture
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: NOT_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "deploy/postgres/init/01_schema.sql"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - APP-ARCH-ROOT-001
  - APP-ARCH-BE-001
  - CAP-APP-IAM-DB-001
  - CAP-APP-CAT-DB-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Documented the split between declared PostgreSQL 16 control-plane tables and in-memory Application Plane dictionaries."
---

# Application Data Architecture (`AS-IS` Memory vs `TARGET` Postgres)

## 1. Scope & Context: `AS-IS` Storage Reality vs `TARGET` PostgreSQL 16 DDL

Although Compose starts PostgreSQL 16 (`deploy/postgres/init/01_schema.sql`) with 5 transactional tables, **zero SQL drivers (`psycopg`, `asyncpg`, `sqlalchemy`) are wired into `src/serving/`**. All Application Plane state (`monitored_instruments`, `backfill_jobs`, `detected_anomalies`, `agent_runs`, `reports`, revoked JWT hashes) is stored ephemerally in process memory inside `PlatformRuntimeContainer` and `JwtSecurityService` and resets on process restart. Only ingestion watermarks persist across restarts (`SQLite WAL` via `src/ingestion/infrastructure/watermark_store.py`, governed by Data Plane `CAP-DP-ING-001`).

## 2. Building Blocks & Table Ownership Across Planes

| Table (`01_schema.sql`) | Owning Capability | `AS-IS` Runtime Store | Key Structural Drift |
|---|---|---|---|
| `users` | `CAP-APP-IAM-001` | None (`POST /auth/token` self-hashes transient password without lookup) | User accounts & API keys are never queried or stored; `api_keys` table absent from `01_schema.sql`! |
| `monitored_instruments` | `CAP-APP-CAT-001` | `runtime.monitored_instruments` dict | No DB read/write; HTTP `PUT` uses upper/lower normalization in memory only |
| `ingestion_watermarks` | `CAP-DP-ING-001` | SQLite `watermarks.db` + `runtime.ingestion_watermarks` dict | SQLite DDL omits `status`/`error_message` present in Postgres DDL |
| `agent_runs` | `CAP-INT-ORC-001` / `CAP-APP-AGT-001` | `runtime.agent_runs` dict + `runtime.reports` dict | `agent_runs.idempotency_key` not in SQL DDL (`runtime` uses `_idempotency_index`) |
| `agent_tool_invocations` | `CAP-INT-ORC-001` | `AgentWorkflowState.evidence_trail` list | In-memory envelopes lost upon restart |
