---
doc_id: TPL-DATA-DB-001
title: "Template: Physical Database & Storage Design"
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
    - "docs/governance/templates/interfaces-and-data/database-design.template.md"
related_docs:
  - GOV-STD-DATA-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created physical database design template covering keys, indexes, transactions, locking, partitioning, retention, migration, rollback, and recovery."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Initial V2 physical database design template."
---

# Template: Physical Database & Storage Design

Instantiated inside `<capability>/data/database-design.md` when the capability owns or modifies physical storage tables.

---

# Physical Database Design: `<Capability Name>`

## 1. Storage Engine & Plane Classification `[REQUIRED]`

- **Workload Type**: `<Application OLTP | Hot Cache | OLAP Warehouse | Lakehouse Medallion>`
- **Target Engine (`TARGET`)**: `<PostgreSQL 16 | ClickHouse | Redis | Iceberg/Parquet>`
- **Actual Engine (`AS-IS`)**: `<Exact verified implementation path & DDL/runtime status>`

## 2. Physical Tables, Keys & Constraints `[REQUIRED]`

| Table / Keyspace | Primary / Sort Key | Constraints / Dedup Semantics | Authoritative DDL Path |
|---|---|---|---|
| `<table>` | `<ORDER BY / PRIMARY KEY>` | `<UNIQUE, CHECK, ReplacingMergeTree FINAL/argMax, Lua monotonic>` | `<deploy/.../01_schema.sql>` |

## 3. Indexing, Partitioning & Retention `[REQUIRED]`

- **Indexes**: `<B-tree / GIN / Skipping index & predicate justification>`
- **Partitioning**: `<Partition key & compaction/file target size>`
- **Retention / TTL**: `<TTL days, snapshot expiry, cold archival>`

## 4. Transactions, Locking & Concurrency `[REQUIRED]`

- **Transaction Scope**: `<Isolation level, unit-of-work, idempotent upsert>`
- **Locking & Contention Risks**: `<Row locks, batch flush intervals, stampede leases>`

## 5. Migration, Rollback, Backup & Recovery `[REQUIRED]`

- **Forward Migration**: `<Zero-downtime DDL / backfill procedure>`
- **Rollback Plan**: `<Deterministic rollback steps without data corruption>`
- **Backup & Restore**: `<Snapshot / Bronze replay verification>`
