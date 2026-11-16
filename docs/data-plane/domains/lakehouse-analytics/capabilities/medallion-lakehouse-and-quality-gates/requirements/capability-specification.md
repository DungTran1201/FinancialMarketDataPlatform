---
doc_id: CAP-DP-LAK-SPEC-001
title: "Capability Specification: Medallion Lakehouse, Quality Gates & Lineage"
doc_type: specification
plane: data-plane
scope_level: capability
domain: lakehouse-analytics
capability_id: CAP-DP-LAK-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/lakehouse/"
related_docs:
  - CAP-DP-LAK-001-ROOT
  - CAP-DP-LAK-RULE-001
requirement_ids:
  - FR-LAK-001
  - FR-LAK-002
  - FR-LAK-003
  - FR-LAK-004
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Specified Bronze archival, Silver MERGE & Iceberg compaction, Stage 8-before-7 DQ blocking, and Gold marts."
---

# Capability Specification: Medallion Lakehouse, Quality Gates & Lineage

## 1. Capability Scope & `AS-IS` Reality `[REQUIRED]`

Executes immutable Bronze archival, idempotent Silver deduplication/compaction, blocking DQ validation, Gold `fct_*` mart aggregation, and 12-node lineage registration locally under `.local_lakehouse/`. MinIO S3, PySpark, PyIceberg REST (`:8181`), Great Expectations, and live `dbt run` remain unimplemented at runtime.

## 2. Functional Requirements `[REQUIRED]`

| Req ID | Requirement Statement | `AS-IS` Evidence | Target / Gap |
|---|---|---|---|
| `FR-LAK-001` | Bronze archiver MUST write immutable ZSTD Parquet partitioned by `bronze/{event_type}/provider={provider}/ingestion_date={date}` using atomic temp file `.replace()`. | `archiver.py:17-72` (local disk) | MinIO S3 unused; `bronze/consumer.py:main()` is a stub |
| `FR-LAK-002` | Silver merge engine MUST deduplicate klines and trades idempotently on natural keys quantized to `Decimal("0.00000001")` and compact Parquet files + Iceberg v2 manifests atomically. | `merge_engine.py:31-376` (`_IO_LOCK` around Parquet) | Silver orderbook merge `NOT_IMPLEMENTED`; `_IO_LOCK` excludes metadata JSON writes (`L358-364`) |
| `FR-LAK-003` | `DataQualityGateEngine` (executed Stage 8 BEFORE Stage 7 Gold in `pipeline.py:319-359`) MUST block Gold promotion (`can_promote_to_gold=False` / `QualityGateBlockedError`) on any `BLOCKING` DQ rule failure. | `gates.py:24-199` | Pure Python `Decimal` rules; `great_expectations` unused |
| `FR-LAK-004` | Gold engine MUST compute `fct_daily_market_summary`, `fct_realized_volatility`, and `fct_orderbook_liquidity` marts and record 10 lineage edges across 12 nodes. | `mart_engine.py:37-266`, `lineage.py:43-201` | dbt has 1 offline SQL model (`fct_daily_market_summary.sql`) only; no Python caller invokes dbt |
