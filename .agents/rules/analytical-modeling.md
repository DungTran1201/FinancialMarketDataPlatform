# Data Rule — Analytical Modeling and Semantic Consistency (`DATA-RULE-007`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-007` |
| **Rule Slug** | `analytical-modeling` |
| **Trigger Scope** | ClickHouse schemas, materialized views, dbt models, Gold marts, and BI/API/Agent-facing metrics |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Enforces explicit dataset grain, natural keys, ClickHouse sorting/partitioning/deduplication semantics, and consistent analytical metric formulas across ClickHouse, dbt Gold marts, Backend APIs, Superset BI, and the Agent Tool Gateway.

## 2. Mandatory Directives

1. **Explicit Grain & Keys**: Declare every analytical model's grain, natural business key, dimensions, measures, units, time semantics, and owner.
2. **ClickHouse Engine & Read Semantics**: Design ClickHouse `PARTITION BY`, `ORDER BY`, TTL, and `ReplacingMergeTree` / `AggregatingMergeTree` query strategies around measured access predicates and asynchronous merge semantics (`FINAL` or `argMax`).
3. **dbt Semantic Ownership**: Define dbt sources, staging/intermediate/mart dependencies, incremental unique keys, schema documentation, and data tests in `src/transformation/dbt/`.
4. **Bounded Serving Queries**: Enforce bounded time ranges (`BoundedTimeRange`) and row caps on all API and Agent Tool Gateway queries.

## 3. Prohibited Actions

- Do not treat `ReplacingMergeTree` as immediate synchronous uniqueness enforcement without `FINAL` or latest-version aggregation in read queries.
- Do not create conflicting definitions of the same financial metric across API, BI, and Agent consumers.
- Do not issue unbounded historical table scans from latency-sensitive API endpoints.

## 4. Verification Mechanism

- ClickHouse DDL review (`deploy/clickhouse/init/01_schema.sql`), dbt build/test checks, bounded query unit tests, and `tools/validators/run_all.py`.

