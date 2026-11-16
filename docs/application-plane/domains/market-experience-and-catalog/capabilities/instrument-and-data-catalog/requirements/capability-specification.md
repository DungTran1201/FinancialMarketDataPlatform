---
doc_id: CAP-APP-CAT-REQ-001
title: "Capability Specification: Instrument & Data Catalog"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-CAT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: business-analyst
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/catalog/presentation/router.py"
    - "frontend/src/modules/data-management/DataManagementModule.ts"
related_docs:
  - CAP-APP-CAT-DOC-001
  - CAP-APP-CAT-DB-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Defined functional requirements and AS-IS memory/fallback gaps for Data Catalog."
---

# Capability Specification: Instrument & Data Catalog

## 1. Capability Scope & `AS-IS` Reality

Manages monitored symbols, evaluates multi-tier freshness lag across hot Redis and OLAP stores, runs ad-hoc Silver/DQ lakehouse runs (`POST /catalog/lakehouse/pipeline`), and powers the `#/data-management` UI view.

## 2. Functional Requirements

| Req ID | Requirement Statement | `AS-IS` Evidence | Target / Gap |
|---|---|---|---|
| `FR-CAT-001` | Operators MUST list (`GET`) and upsert (`PUT`) monitored instruments persistently across restarts. | `catalog/router.py:23-59` | Stored solely in `runtime.monitored_instruments` dict; zero Postgres writes; unauthenticated (`SEC-AUDIT-003`). |
| `FR-CAT-002` | System MUST report `hot_redis_lag_ms`, `clickhouse_lag_ms`, and `is_healthy` per monitored instrument relative to `market_staleness_threshold_ms`. | `catalog/router.py:61-78` | Implemented over runtime stores (`5000` ms default threshold). |
| `FR-CAT-003` | Operators MUST be able to trigger ad-hoc Bronze->Silver merge & DQ validation via `POST /catalog/lakehouse/pipeline`. | `catalog/router.py:80-124` | Reads `kafka_broker._topics` directly if offsets committed; klines only (omits trades merge in this endpoint). |
| `FR-CAT-004` | `#/data-management` MUST display real lineage/watermarks/DQ rules/Gold marts without silently substituting fake graphs on empty API responses. | `DataManagementModule.ts`, `catalog.service.ts` | `catalog.service.getLineage()` falls back to static 8-node/4-edge mock (`COMPAT-007`). |
