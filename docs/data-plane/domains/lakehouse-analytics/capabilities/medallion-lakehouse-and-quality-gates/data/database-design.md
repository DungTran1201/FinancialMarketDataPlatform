---
doc_id: CAP-DP-LAK-DB-001
title: "Physical Storage Design: Local Parquet Tiers, Custom Iceberg JSON & dbt SQL"
doc_type: specification
plane: data-plane
scope_level: capability
domain: lakehouse-analytics
capability_id: CAP-DP-LAK-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/lakehouse/bronze/archiver.py"
    - "src/lakehouse/silver/merge_engine.py"
    - "src/lakehouse/gold/mart_engine.py"
    - "deploy/iceberg/catalog-config.yaml"
    - "src/lakehouse/gold/dbt/models/marts/fct_daily_market_summary.sql"
related_docs:
  - CAP-DP-LAK-MOD-001
  - DIAG-DP-LAK-ERD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Documented actual local .local_lakehouse/ Parquet files, Iceberg JSON manifests, and single offline dbt SQL file."
---

# Physical Storage Design: Local Parquet Tiers, Custom Iceberg JSON & dbt SQL

Derived ERD: [lakehouse-erd.md](lakehouse-erd.md) (`DIAG-DP-LAK-ERD-001`).

## 1. Physical Storage Layout (`AS-IS`: `.local_lakehouse/`) `[REQUIRED]`

- **Bronze**: `.local_lakehouse/bronze/{event_type}/provider={provider}/ingestion_date={YYYY-MM-DD}/part_{event_type}_{batch_id}.parquet` (`ZSTD`).
- **Silver**: `.local_lakehouse/silver/{table_name}/silver_{table_name}.parquet` or `compacted_silver_{table_name}.parquet` + `metadata/v{snapshot_id}.metadata.json` (`"format-version": 2`, `parent_snapshot_id` chaining, `version-hint.text`, max `5` retained).
- **Gold**: `.local_lakehouse/gold/{mart_name}/gold_{mart_name}.parquet` (`ZSTD`).

## 2. Target Infrastructure & Conflicts (`TARGET`) `[REQUIRED]`

- **MinIO & Iceberg REST Conflicts**: `deploy/object-storage/init-buckets.sh` creates `lakehouse-{bronze,silver,gold,checkpoints}` whereas `.env.example:62` declares `LAKEHOUSE_BUCKET=market-data`; `deploy/iceberg/catalog-config.yaml` references `http://iceberg-rest:8181` (absent from `docker-compose.yml`).
- **dbt Project (`src/lakehouse/gold/dbt/`)**: Configures `type: clickhouse` incremental `ReplacingMergeTree` (`fct_daily_market_summary.sql` only, parsed offline by dbt `1.12.7`).
