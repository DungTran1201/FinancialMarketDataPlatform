---
doc_id: DP-DOM-LAK-001
title: "Domain: Lakehouse & Analytical Processing"
doc_type: index
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
related_docs:
  - DP-ROOT-001
  - DP-DOM-LAK-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Registered lakehouse-analytics domain and CAP-DP-LAK-001."
---

# Domain: Lakehouse & Analytical Processing

Owns Bronze ZSTD Parquet archival, Silver deduplication and snapshot manifests, blocking Data Quality validation gates, Gold financial marts, offline `dbt` SQL models, 12-node lineage registration, and the 12-stage `DataPlatformV01Pipeline` orchestrator (`src/lakehouse/`).

- [domain-specification.md](domain-specification.md) (`DP-DOM-LAK-SPEC-001`)
- Capabilities:
  - `CAP-DP-LAK-001`: [medallion-lakehouse-and-quality-gates](capabilities/medallion-lakehouse-and-quality-gates/README.md) (`PARTIALLY_IMPLEMENTED` — Local ZSTD Parquet & custom JSON Iceberg manifests; MinIO/Spark/live dbt unused)
