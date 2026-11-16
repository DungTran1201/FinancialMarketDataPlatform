---
doc_id: TPL-DIAG-ERD-001
title: "Template: Entity-Relationship Diagram (ERD)"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: database-architect
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/diagrams/erd-diagram.template.md"
related_docs:
  - GOV-STD-DIAG-001
  - GOV-STD-DATA-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Crow's Foot ERD diagram template aligned with logical and physical data standards."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Initial V2 ERD diagram template."
---

# Template: Entity-Relationship Diagram (ERD)

Use for capabilities that own relational tables, analytical schemas, or cross-entity key structures (`MEDIUM` / `HIGH_CRITICAL` DB capabilities). Derived strictly from Data Model and Database Design docs. When instantiated, set `doc_type: diagram` and `source_of_truth.is_authoritative: false`.

---

# Diagram: `<Domain / Schema Name> ERD`

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-<SCOPE>-NNN` |
| **Title & Purpose** | `<Title — One-sentence data model scope>` |
| **Model Level** | `<Logical | Physical>` |
| **Owner Role & Scope** | `database-architect / <plane|capability>` |
| **Authoritative Source** | `[<Data Model / DB Design>](<relative/path/to/data-model.md>)` (`<DOC-ID>`) |
| **Notation** | `Mermaid erDiagram` (`Crow's Foot`) |
| **Version & Status** | `<X.Y.Z> — <DRAFT|IN_REVIEW|APPROVED|DEPRECATED>` |

## 2. Diagram `[REQUIRED]`

```mermaid
erDiagram
    PARENT_ENTITY ||--o{ CHILD_RECORD : "owns"
    PARENT_ENTITY {
        string entity_id PK "Stable business identifier"
        string status "Lifecycle state"
        datetime created_at "UTC timestamp"
    }
    CHILD_RECORD {
        string record_id PK "Surrogate or natural key"
        string entity_id FK "References PARENT_ENTITY"
        decimal amount "Exact Decimal string/numeric (no float)"
        datetime event_time "Event timestamp (UTC)"
    }
```

## 3. Legend `[REQUIRED]`

- **`||--o{`**: One-to-zero-or-many cardinality relationship.
- **`PK` / `FK` / `UK`**: Primary Key, Foreign Key, or Unique constraint.
- **Note**: Analytical stores without enforced foreign keys (e.g., ClickHouse / Iceberg) MUST still label logical join keys as `FK (logical)` in descriptions.
