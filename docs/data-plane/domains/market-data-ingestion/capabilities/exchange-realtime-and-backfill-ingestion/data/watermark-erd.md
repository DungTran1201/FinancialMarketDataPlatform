---
doc_id: DIAG-DP-ING-ERD-001
title: "Diagram: Ingestion Watermark Physical Schemas (SQLite vs Postgres)"
doc_type: diagram
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/data-plane/domains/market-data-ingestion/capabilities/exchange-realtime-and-backfill-ingestion/data/database-design.md"
related_docs:
  - CAP-DP-ING-DB-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Derived ERD comparing AS-IS SQLite schema with TARGET Postgres DDL."
---

# Diagram: Ingestion Watermark Physical Schemas

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-ING-ERD-001` |
| **Title & Purpose** | Side-by-side schema diagram showing AS-IS SQLite `ingestion_watermarks` and TARGET Postgres `ingestion_watermarks` |
| **Model Level** | Physical (`AS-IS` + `TARGET` Comparison) |
| **Owner Role & Scope** | `database-architect / CAP-DP-ING-001` |
| **Authoritative Source** | [database-design.md](database-design.md) (`CAP-DP-ING-DB-001`) |
| **Notation** | `Mermaid erDiagram` (`Crow's Foot`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
erDiagram
    SQLITE_INGESTION_WATERMARKS {
        string provider PK "Part of composite PK"
        string symbol PK "Part of composite PK"
        string interval PK "Part of composite PK (1m, 5m, 1h)"
        string last_open_time "ISO UTC string"
        string updated_at "ISO UTC string"
        string status "SYNCED | BACKFILLING | GAP_DETECTED"
    }
    POSTGRES_INGESTION_WATERMARKS_TARGET {
        uuid watermark_id PK "01_schema.sql UUID"
        string provider UK "UNIQUE(provider, symbol, dataset)"
        string symbol UK "UNIQUE(provider, symbol, dataset)"
        string dataset UK "UNIQUE(provider, symbol, dataset)"
        datetime last_synced_timestamp "TIMESTAMPTZ NOT NULL"
        string status "IDLE | RUNNING | FAILED | COMPLETED"
        datetime updated_at "TIMESTAMPTZ"
    }
```

## 3. Legend `[REQUIRED]`

- `SQLITE_INGESTION_WATERMARKS`: Active `AS-IS` store initialized in `src/ingestion/infrastructure/watermark_store.py`.
- `POSTGRES_INGESTION_WATERMARKS_TARGET`: Unwired `TARGET` DDL in `deploy/postgres/init/01_schema.sql:30-39` with mismatched `dataset` key and status constraint.
