---
doc_id: DIAG-APP-CAT-ERD-001
title: "ERD Diagram: `monitored_instruments` & Watermark Key Mapping"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-CAT-001
status: IN_REVIEW
implementation_status: NOT_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/market-experience-and-catalog/capabilities/instrument-and-data-catalog/data/database-design.md"
related_docs:
  - CAP-APP-CAT-DB-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Rendered ERD showing Postgres monitored_instruments and natural key coupling to ingestion_watermarks."
---

# ERD Diagram: `monitored_instruments` & Watermark Key Mapping

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-CAT-ERD-001` |
| **Title & Purpose** | `monitored_instruments` Physical Schema & Natural `(provider, symbol)` Relation |
| **Owner Role & Scope** | `database-architect / CAP-APP-CAT-001` |
| **Authoritative Source** | [database-design.md](database-design.md) (`CAP-APP-CAT-DB-001`) |
| **Notation** | `Mermaid erDiagram` (`Crow's Foot`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
erDiagram
    monitored_instruments {
        uuid instrument_id PK
        text provider
        text symbol
        text base_asset
        text quote_asset
        text status
        jsonb enabled_streams
        timestamptz updated_at
    }
    ingestion_watermarks {
        text provider PK
        text symbol PK
        text interval PK
        timestamptz last_open_time
        text status
    }

    monitored_instruments ||--o{ ingestion_watermarks : "natural key (provider, symbol) [Target]"
```

## 3. Legend

- **Unwired Relationship**: `monitored_instruments` is defined in `01_schema.sql` without runtime SQL queries; `ingestion_watermarks` uses SQLite WAL `AS-IS`.
