---
name: analytics-engineering-dbt-clickhouse
description: ClickHouse OLAP schemas, ReplacingMergeTree views, and dbt Gold marts.
---

# Skill: ClickHouse & dbt Analytics Engineering (`SKILL-017`)

## 1. Description

Design ClickHouse analytical schemas (`ReplacingMergeTree`, `AggregatingMergeTree`) and dbt Gold models (`src/lakehouse/gold/dbt/`) with explicit grain, metric semantics, incremental correctness, tests, and bounded query performance.

## 2. Trigger Conditions

- Creating or updating ClickHouse tables/views, materialized views, dbt sources/models/tests, Gold marts, analytical metrics, or BI/API/Agent query patterns (`analytics-engineer`).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/data-plane/architecture/data-storage-architecture.md`, `docs/data-plane/shared-contracts/data-contract.yaml`, `docs/data-plane/domains/event-streaming/capabilities/realtime-hot-state-and-olap-projection/data/database-design.md`, `docs/data-plane/domains/lakehouse-analytics/capabilities/medallion-lakehouse-and-quality-gates/data/database-design.md`, `deploy/clickhouse/init/01_schema.sql`, `src/lakehouse/gold/dbt/dbt_project.yml`.

## 4. Preconditions

1. Owning capability `capability.yaml` read; dataset grain, natural business key, time dimension, measure units, metric formula, freshness target, and owning layer declared.

## 5. Execution Procedure

1. Identify primary query predicates and data volume; choose ClickHouse `PARTITION BY` and `ORDER BY` keys accordingly.
2. Select engine/version columns (`ReplacingMergeTree` / `AggregatingMergeTree`) and deduplication read strategy (`FINAL` or `argMax`); explicitly account for asynchronous background merges.
3. Keep raw high-volume facts, rollups, and marts separate; design TTL policies from business and replay/retention requirements.
4. In dbt (`src/lakehouse/gold/dbt/`), declare sources, staging/intermediate/mart layers, materializations, incremental unique keys, and schema documentation.
5. Keep Gold business logic in dbt Core per `.agents/config/data-platform-boundaries.yaml`; use PySpark only for Bronze-to-Silver standardization/backfill.
6. Add dbt data tests for uniqueness, non-null, relationships, accepted values, and custom financial invariants.
7. Validate incremental runs against full-refresh outputs on representative time windows.
8. Benchmark representative ClickHouse query plans and inspect scan size, partition pruning, memory, and latency.
9. Synchronize owning capability `data/` docs and `docs/data-plane/shared-contracts/data-contract.yaml`, then run `scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- ClickHouse DDL updates (`deploy/clickhouse/`), dbt source/model/schema/test files (`src/lakehouse/gold/dbt/`), semantic definitions, benchmarks, and updated capability `data/` docs under `docs/data-plane/`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/unit/ tests/data_quality/ -v
```

## 8. Failure Handling

- Do not publish partial Gold data; retain the previous valid model/table state and surface failed runs and affected partitions.
- Record any unresolved metric formula or grain question as `[OPEN]` in `capability.yaml`.

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
