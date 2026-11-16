---
doc_id: CAP-DP-LAK-TS-001
title: "Test Scenarios: Medallion Lakehouse & Quality Gates"
doc_type: specification
plane: data-plane
scope_level: capability
domain: lakehouse-analytics
capability_id: CAP-DP-LAK-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: qa-lead
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/data_quality/test_medallion_quality_gates.py"
    - "tests/e2e/test_data_platform_v01_e2e.py"
related_docs:
  - CAP-DP-LAK-SPEC-001
requirement_ids:
  - TS-LAK-001
  - TS-LAK-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Documented Bronze->Silver idempotent merge, Iceberg snapshot chaining, DQ blocking, and Gold Decimal verification."
---

# Test Scenarios: Medallion Lakehouse & Quality Gates

## 1. Scenario Matrix `[REQUIRED]`

| Scenario ID | Linked FR / RULE | Scenario Summary | Expected Outcome | Environment |
|---|---|---|---|---|
| `TS-LAK-001` | `FR-LAK-003`, `RULE-LAK-001` | Submit Silver klines with `high < low` & duplicate keys to `DataQualityGateEngine` & `DataPlatformV01Pipeline`. | `DQ-KLINE-001` & `DQ-KLINE-003` fail; `can_promote_to_gold=False` (or raises `QualityGateBlockedError`). | Local temp Parquet (`test_medallion_quality_gates.py`, `test_data_platform_v01_e2e.py`) |
| `TS-LAK-002` | `FR-LAK-001`, `FR-LAK-002`, `FR-LAK-004` | Archive Bronze Parquet -> merge twice -> compact twice -> build Gold marts. | Deduplicated `len == 2`, `files_after_compaction == 1`, valid `parent_snapshot_id` chain & `version-hint.text`, Gold `Decimal` parseable. | Local temp filesystem |

## 2. Environment Disclosure

MinIO S3, Spark, Iceberg REST catalog, and dbt ClickHouse execution remain untested (`GAP-QA-001`).
