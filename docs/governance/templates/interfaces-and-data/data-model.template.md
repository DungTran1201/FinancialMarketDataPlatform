---
doc_id: TPL-DATA-MOD-001
title: "Template: Conceptual & Logical Data Model"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: database-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/interfaces-and-data/data-model.template.md"
related_docs:
  - GOV-STD-DATA-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created logical data model template separating business entities and attributes from physical storage implementation."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Initial V2 logical data model template."
---

# Template: Conceptual & Logical Data Model

Technology-neutral logical model (`<capability>/data/data-model.md`). Physical indexes, partitions, and DDL belong in [database-design.template.md](database-design.template.md).

---

# Logical Data Model: `<Domain or Capability Name>`

## 1. Conceptual Domain Scope & ERD Reference `[REQUIRED]`

- **Domain / Plane**: `<domain>` / `<plane>`
- **Diagram Reference**: `[<erd-diagram.md>](<erd-diagram.md>)` (`DIAG-...`, `OPTIONAL` for `LOW` risk)

## 2. Logical Entities & Natural Keys `[REQUIRED]`

| Entity | Grain (1 row represents...) | Natural / Business Key | Lifecycle / Mutability (`Append-Only | Versioned | Mutable OLTP`) |
|---|---|---|---|
| `<Entity>` | `<Exact row grain>` | `(<col1>, <col2>)` | `<Mutability>` |

## 3. Attribute Dictionary `[REQUIRED]`

| Entity | Attribute | Logical Type & Precision | Nullable | Units / Domain Constraints |
|---|---|---|---|---|
| `<Entity>` | `<attr>` | `<Decimal(38,18) / UTC Timestamp / Enum>` | `No` | `<Constraint>` |

## 4. Lineage & Quality Rules `[CONDITIONAL: Required for Data Plane datasets]`

- Reference canonical `data-contract.yaml` and quality rules (`DQ-...`).
