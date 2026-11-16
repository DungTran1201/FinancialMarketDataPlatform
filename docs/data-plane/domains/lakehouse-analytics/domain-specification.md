---
doc_id: DP-DOM-LAK-SPEC-001
title: "Domain Specification: Lakehouse & Analytical Processing"
doc_type: specification
plane: data-plane
scope_level: domain
domain: lakehouse-analytics
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
    - "deploy/iceberg/catalog-config.yaml"
related_docs:
  - DP-DOM-LAK-001
  - CAP-DP-LAK-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Defined Medallion Bronze->Silver->Gold bounded context cleanly without overclaiming Spark, Iceberg REST, or live dbt."
---

# Domain Specification: Lakehouse & Analytical Processing

## 1. Bounded Context & Medallion Boundaries `[REQUIRED]`

Owns durable columnar ZSTD Parquet tiers (`.local_lakehouse/`), natural-key deduplication, snapshot compaction, `DQ-KLINE-*` / `DQ-TRADE-*` quality promotion gates, Gold `fct_*` marts, and 12-node lineage metadata. Refer to [data-contract.yaml](../../shared-contracts/data-contract.yaml) for canonical dataset natural keys.

## 2. Technology Reality Statement

Despite legacy references and docstrings mentioning Apache Spark, PyIceberg, Great Expectations, and MinIO S3, all runtime Bronze/Silver/Gold IO executes via Python `pyarrow.parquet`, local JSON Iceberg v2 manifests, pure-Python `Decimal` math, and an in-memory lineage catalog (`GAP-DATA-001`). Only one dbt SQL model (`fct_daily_market_summary.sql`) exists on disk (parsed offline, un-invoked by Python code).
