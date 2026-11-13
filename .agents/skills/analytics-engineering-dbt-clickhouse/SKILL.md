---
name: analytics-engineering-dbt-clickhouse
description: "Design ClickHouse analytical schemas and dbt Gold models with explicit grain, metric semantics, incremental correctness, tests and query performance."
---

# Skill: ClickHouse & dbt Analytics Engineering (`SKILL-017`)

## 1. Description

Design ClickHouse analytical schemas and dbt Gold models with explicit grain, metric semantics, incremental correctness, tests, and query performance.

## 2. Trigger Conditions

- Use when creating or changing ClickHouse tables/views, materialized views, dbt sources/models/tests, Gold marts, analytical metrics, or BI/API/Agent query patterns.
- Invoked by Agent role `analytics-engineer` (`.agents/agents/analytics-engineer.md`).

## 3. Authoritative Inputs

- `AGENTS.md` and target directory `README.md`
- `docs/specifications/data-dictionary.md` and `data-requirements.md`
- `docs/architecture/adr/ADR-003-storage-strategy.md` and `ADR-005-query-and-caching-strategy.md`
- `deploy/clickhouse/init/01_schema.sql` and `src/transformation/dbt/dbt_project.yml`
- Relevant canonical models in `models/domain/` and `models/testing/`

## 4. Preconditions

1. Target directory `README.md` has been read in full.
2. Dataset grain, natural business key, time dimension, measure units, metric formula, freshness target, and owning layer have been declared.

## 5. Execution Procedure

1. Identify primary query predicates and data volume; choose ClickHouse `PARTITION BY` and `ORDER BY` keys accordingly.
2. Select engine/version columns (`ReplacingMergeTree` / `AggregatingMergeTree`) and deduplication read strategy (`FINAL` or `argMax`); explicitly account for asynchronous background merges.
3. Keep raw high-volume facts, rollups, and marts separate; design TTL policies from business and replay/retention requirements.
4. In dbt (`src/transformation/dbt/`), declare sources, staging/intermediate/mart layers, materializations, incremental unique keys, and schema documentation.
5. Keep Gold business logic in dbt Core per `.agents/config/data-platform-boundaries.yaml`; use PySpark only for Bronze-to-Silver standardization/backfill.
6. Add dbt data tests for uniqueness, non-null, relationships, accepted values, and custom financial invariants.
7. Validate incremental runs against full-refresh outputs on representative time windows.
8. Benchmark representative ClickHouse query plans and inspect scan size, partition pruning, memory, and latency.
9. Synchronize `docs/specifications/data-dictionary.md`, `models/domain/`, lineage, and API/BI/Agent consumers, then run `tools/validators/run_all.py`.

## 6. Output Artifacts

- ClickHouse DDL updates (`deploy/clickhouse/`), dbt source/model/schema/test files (`src/transformation/dbt/`), semantic definitions, benchmarks, and updated canonical models in `models/domain/`.

## 7. Validation

```powershell
python tools/validators/run_all.py
python -m unittest discover -s tests -v
```

## 8. Failure Handling

- Do not publish partial Gold data; retain the previous valid model/table state and surface failed runs and affected partitions.
- Record any unresolved metric formula or grain question as `[OPEN QUESTION]`.

## 9. Restrictions

- No unbounded API or Agent queries (`BoundedTimeRange` required).
- No floating-point financial persistence (`Decimal` required).
- No silent grain or metric formula changes.
- No assumption that `ReplacingMergeTree` deduplication is synchronous at write time.

## 10. Related Skills

- `lakehouse-medallion`
- `financial-data-quality`
- `data-governance-lineage`
- `data-platform-testing-recovery`

