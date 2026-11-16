---
doc_id: CAP-DP-ING-DB-001
title: "Physical Database Design: Ingestion Watermark Store (SQLite AS-IS vs Postgres TARGET)"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/infrastructure/watermark_store.py"
    - "deploy/postgres/init/01_schema.sql"
related_docs:
  - CAP-DP-ING-MOD-001
  - DIAG-DP-ING-ERD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Documented physical SQLite WAL watermark DDL alongside Postgres schema incompatibility requiring migration alignment."
---

# Physical Database Design: Ingestion Watermark Store

Derived ERD: [watermark-erd.md](watermark-erd.md) (`DIAG-DP-ING-ERD-001`).

## 1. `AS-IS` Physical Store: SQLite WAL (`watermark_store.py:15-40`) `[REQUIRED]`

- **Location**: `.local_storage/control_watermarks.db` (`PRAGMA journal_mode=WAL;`). Closed cleanly on FastAPI lifespan shutdown (`runtime.py:185-187`).
- **Table `ingestion_watermarks`**:
  - Columns: `provider TEXT NOT NULL`, `symbol TEXT NOT NULL`, `interval TEXT NOT NULL`, `last_open_time TEXT NOT NULL`, `updated_at TEXT NOT NULL`, `status TEXT NOT NULL`
  - Primary Key: `PRIMARY KEY (provider, symbol, interval)`
  - Upsert semantics: `INSERT INTO ingestion_watermarks ... ON CONFLICT(provider, symbol, interval) DO UPDATE SET ...`

## 2. `TARGET` Physical Store & Migration Gap: PostgreSQL (`deploy/postgres/init/01_schema.sql:30-39`) `[REQUIRED]`

- **Postgres Table `ingestion_watermarks`**:
  - Columns: `watermark_id UUID PRIMARY KEY`, `provider VARCHAR(32) NOT NULL`, `symbol VARCHAR(32) NOT NULL`, `dataset VARCHAR(64) NOT NULL`, `last_synced_timestamp TIMESTAMPTZ NOT NULL`, `status VARCHAR(32) NOT NULL CHECK (status IN ('IDLE', 'RUNNING', 'FAILED', 'COMPLETED'))`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
  - Unique Key: `UNIQUE (provider, symbol, dataset)`
- **Schema Conflict (`OPEN` Migration Prerequisite)**: Postgres uses `dataset` + `IDLE|RUNNING|FAILED|COMPLETED`, whereas Python `IngestionWatermarkStore` uses `interval` + `SYNCED|BACKFILLING|GAP_DETECTED` and has zero `asyncpg`/`sqlalchemy` implementation.

## 3. Migration & Rollback Strategy `[REQUIRED]`

- Until Postgres adapter migration is implemented, rollbacks revert to `.local_storage/control_watermarks.db` backup copy; target SQL DDL additions require explicit idempotent `ALTER TABLE` scripts cleanly versioned before container cutover (`OPEN`).
