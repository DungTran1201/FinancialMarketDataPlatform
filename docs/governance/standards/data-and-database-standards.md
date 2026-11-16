---
doc_id: GOV-STD-DATA-001
title: "Data Architecture, Modeling & Database Documentation Standards"
doc_type: standard
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/standards/data-and-database-standards.md"
related_docs:
  - GOV-STD-API-001
  - GOV-STD-NFR-001
  - GOV-STD-SEC-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established standards separating conceptual, logical, and physical data models, application OLTP vs Data Plane storage, migrations, lineage, and quality gates."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Initial Documentation V2 data and database modeling standard."
---

# Data Architecture, Modeling & Database Documentation Standards

## 1. Three-Level Data Modeling & Plane Separation

1. **Logical vs. Physical Separation**: Authors MUST separate:
   - **Conceptual Model**: High-level bounded-context business entities and relationships.
   - **Logical Data Model** ([data-model.template.md](../templates/interfaces-and-data/data-model.template.md)): Technology-neutral entities, attributes, data types, domain invariants, natural keys, and cardinality (`ERD`).
   - **Physical Storage Design** ([database-design.template.md](../templates/interfaces-and-data/database-design.template.md)): Engine-specific DDL mapping, indexes, partition keys, sort keys, TTLs, compaction, and locking.
2. **Application Persistence vs. Data Plane Storage**: Documentation MUST explicitly distinguish:
   - **Application / Control OLTP Persistence** (e.g., PostgreSQL / SQLite state for IAM, instruments, watermarks, agent run state).
   - **Data Plane Storage Tiers** (ephemeral hot cache, streaming event logs, analytical OLAP tables, immutable Bronze/Silver/Gold lakehouse datasets).

## 2. Mandatory Database Design Elements

Every physical database or lakehouse table design MUST document:

- **Entity & Attribute Dictionary**: Column name, exact type/precision (for financial values, decimal scale/precision MUST be explicit; binary floats MUST NOT be used silently), nullability, units, and UTC time semantics.
- **Keys & Constraints**: Primary keys, natural deduplication keys, foreign keys, `CHECK` constraints, and uniqueness guarantees (including whether uniqueness is synchronous ACID or asynchronous merge-time such as `ReplacingMergeTree`).
- **Indexing & Sorting Strategy**: Exact B-tree/GIN indexes or columnar `ORDER BY` / Z-order keys justified by measured read predicates.
- **Transactions, Consistency & Concurrency**: Isolation level, unit-of-work boundaries, idempotent upsert/Lua/merge semantics, and row/table locking behavior.
- **Partitioning & Retention**: Partition expression, file size / compaction targets, TTL expiration, snapshot retention, and cold archival tiering.
- **Migration & Rollback**: Forward schema change steps, backward compatibility during rolling deployments, backfill strategy, and deterministic rollback procedure.
- **Backup & Recovery**: Snapshot frequency, point-in-time recovery or replay-from-Bronze procedure, and verified restore test evidence.

## 3. Data Contracts, Lineage & Quality Requirements

1. **Data Contracts**: Cross-stage or cross-plane datasets MUST declare an owner, schema, freshness SLA, natural key, and breaking-change policy in [data-contract.template.yaml](../templates/interfaces-and-data/data-contract.template.yaml).
2. **End-to-End Lineage**: Every analytical or derived dataset MUST document upstream source(s), transformation job/engine, target sink(s), and downstream consumers (API, BI, Agent).
3. **Data Quality Rules**: Every dataset MUST declare executable quality checks (schema validity, completeness, uniqueness, freshness, domain invariants), severity (`BLOCKING` vs `WARNING`), and promotion blocking behavior when critical checks fail.
4. **Evidence Linking**: Database and pipeline changes MUST trace to requirements (`FR`/`NFR`/`RULE`) and verification tests (`TC`) without assuming declared SQL/YAML files match runtime behavior until verified.
