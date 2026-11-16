---
name: lakehouse-medallion
description: MinIO/Iceberg Bronze-Silver-Gold tables, PySpark standardization, and compaction.
---

# Skill: Lakehouse Medallion Engineering (`SKILL-025`)

## 1. Description

Engineer MinIO/S3, Parquet, and Apache Iceberg lakehouse layers with immutable Bronze (`src/lakehouse/bronze/`), standardized Silver (`src/lakehouse/silver/merge_engine.py`), PySpark backfills, and safe table maintenance.

## 2. Trigger Conditions

- MinIO/object storage, Parquet file layout, Apache Iceberg catalog/table changes, Bronze archiving, Silver merge, PySpark batch jobs, compaction, snapshot retention, or historical backfills (`lakehouse-engineer`).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/data-plane/domains/lakehouse-analytics/capabilities/medallion-lakehouse-and-quality-gates/capability.yaml`, `docs/data-plane/architecture/data-storage-architecture.md`, `docs/data-plane/shared-contracts/data-contract.yaml`, `src/lakehouse/silver/merge_engine.py`, `deploy/iceberg/catalog-config.yaml`.

## 4. Preconditions

1. Owning capability `capability.yaml` read; Medallion layer (`Bronze` or `Silver`), table owner, natural key, version column, event-time semantics, and recovery plan confirmed.

## 5. Execution Procedure

1. Define Iceberg catalog/namespace/table ownership and schema with explicit `Decimal` precision, nullability, units, and UTC semantics.
2. Keep Bronze append-only and source-preserving in MinIO/local Parquet, recording `event_id`, `schema_version`, `ingested_at`, and source partition/offset metadata.
3. Use deterministic file/object naming so retry and offset-commit crash windows remain idempotent.
4. Configure Parquet compression (`ZSTD` / `Snappy`), target file size, and partition transforms without high-cardinality partition explosion.
5. Implement Silver typing, UTC normalization, and deterministic deduplication via PySpark Iceberg `MERGE INTO` (`SilverMergeJobSpec` in `src/lakehouse/silver/merge_engine.py`).
6. Integrate data quality checks (`QualityExpectationRule`) before promoting Silver tables.
7. Implement bounded backfill, checkpointing, compaction, and snapshot maintenance with dry-run controls, synchronize `docs/data-plane/domains/lakehouse-analytics/`, and run `scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- Iceberg table definitions, Bronze writer updates (`src/lakehouse/bronze/`), `Bronze -> Silver` jobs (`src/lakehouse/silver/`), updated Data Plane lakehouse capability docs (`data-model.md`, `database-design.md`, `data-contract.yaml`), and lakehouse runbooks.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/data_quality/ tests/e2e/ -v
```

## 8. Failure Handling

- Keep table commits atomic at the Iceberg metadata layer, preserve raw Bronze replay inputs, and block downstream promotion on `CRITICAL` quality failures.

## 9. Restrictions

- Do not mutate Bronze into a business-cleaned table.
- Do not place Gold business metric SQL into PySpark where dbt Core owns the semantic layer.
- Do not expire snapshots or overwrite historical partitions without human approval.

## 10. Related Skills

- `financial-data-quality`
- `data-governance-lineage`
- `dataops-observability`
- `data-platform-testing-recovery`
