---
doc_id: CAP-APP-CAT-UC-002
title: "Use Case UC-CAT-002: Inspect Freshness, Lineage, Watermarks & Ad-Hoc Lakehouse Pipeline"
doc_type: specification
plane: application-plane
scope_level: use-case
domain: market-experience-and-catalog
capability_id: CAP-APP-CAT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/catalog/presentation/router.py"
    - "frontend/src/modules/data-management/DataManagementModule.ts"
related_docs:
  - CAP-APP-CAT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented catalog freshness, DataManagementModule explorer tabs, and manual lakehouse trigger."
---

# Use Case UC-CAT-002: Inspect Freshness, Lineage, Watermarks & Ad-Hoc Lakehouse Pipeline

## 1. Main Inspection & Pipeline Flows

1. **Freshness Monitoring**: Caller/UI invokes `GET /api/v1/catalog/freshness?provider=binance`; backend computes hot Redis lag vs ClickHouse lag for every instrument in memory and compares against `market_staleness_threshold_ms`.
2. **Governance & Storage Explorer (`#/data-management`)**: `DataManagementModule.ts` queries `/observability/storage`, `/data-platform/v01/watermarks`, `/data-platform/v01/lineage`, and `/data-platform/v01/gold/{mart_name}`. (*Gap*: `CatalogService.getLineage()` injects a static 8-node fallback when backend returns empty.)
3. **Ad-Hoc Pipeline Run (`POST /catalog/lakehouse/pipeline`)**: Polls `market.raw.klines.v1` (falling back to scanning `_topics` internally if empty!), archives Bronze Parquet, merges Silver klines Iceberg v2, runs DQ checks (`can_promote_to_gold`), and returns counts.

## 2. Exception Flows & Target Fixes

- **Empty Topic Behavior**: Returns `bronze_files_written: 0` with `dq_passed: true` rather than an error.
- **Target Scope**: Enforce `catalog:write` RBAC before `/lakehouse/pipeline` and remove mock lineage fallback in `catalog.service.ts`.
