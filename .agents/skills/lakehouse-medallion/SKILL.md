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

- `AGENTS.md`, target `README.md`, `docs/architecture/04-data-platform-architecture.md`, `07-data-storage-and-modeling.md`, `ADR-002`, `ADR-003`, `src/lakehouse/silver/merge_engine.py`, `docs/specifications/data-contracts.md`, `models/domain/`, `models/data-platform/`.

## 4. Preconditions

1. Target `README.md` read; Medallion layer (`Bronze` or `Silver`), table owner, natural key (`idempotency_key`), version column, event-time semantics, and recovery plan confirmed.

## 5. Execution Procedure

1. Define Iceberg catalog/namespace/table ownership and schema with explicit `Decimal` precision, nullability, units, and UTC semantics.
2. Keep Bronze append-only and source-preserving in MinIO (`Parquet`), recording `event_id`, `schema_version`, `ingested_at`, and source partition/offset metadata.
3. Use deterministic file/object naming so retry and offset-commit crash windows remain idempotent.
4. Configure Parquet compression (`ZSTD` / `Snappy`), target file size, and partition transforms without high-cardinality partition explosion.
5. Implement Silver typing, UTC normalization, and deterministic deduplication via PySpark Iceberg `MERGE INTO` (`SilverMergeJobSpec` in `src/lakehouse/silver/merge_engine.py`).
6. Integrate data quality checks (`QualityExpectationRule`) before promoting Silver tables.
7. Implement bounded backfill, checkpointing, compaction, and snapshot maintenance with dry-run controls, then run `tools/validators/run_all.py`.

## 6. Output Artifacts

- Iceberg table definitions, Bronze writer updates (`src/lakehouse/bronze/`), `Bronze -> Silver` jobs (`src/lakehouse/silver/`), updated domain/data-platform models (`models/`), and lakehouse runbooks.

## 7. Validation

```powershell
python tools/validators/run_all.py
python -m unittest discover -s tests -v
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

