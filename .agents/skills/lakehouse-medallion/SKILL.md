---
name: lakehouse-medallion
description: "Engineer MinIO/S3, Parquet and Iceberg lakehouse layers with immutable Bronze, standardized Silver, Spark backfills and safe table maintenance."
---

# Skill: Lakehouse Medallion Engineering (`SKILL-025`)

## 1. Description

Engineer MinIO/S3, Parquet, and Apache Iceberg lakehouse layers with immutable Bronze, standardized Silver, PySpark backfills, and safe table maintenance.

## 2. Trigger Conditions

- Use for MinIO/object storage, Parquet file layout, Apache Iceberg catalog/table changes, Bronze archiving (`consumer-lakehouse-bronze`), Silver merge (`SilverMergeJobSpec`), PySpark batch jobs, compaction, snapshot retention, and historical backfills.
- Invoked by Agent role `lakehouse-engineer` (`.agents/agents/lakehouse-engineer.md`).

## 3. Authoritative Inputs

- `AGENTS.md` and target directory `README.md`
- `docs/architecture/04-data-platform-architecture.md`, `07-data-storage-and-modeling.md`, and `ADR-002` / `ADR-003`
- `src/consumers/lakehouse_bronze/main.py` and `src/processing/spark/bronze_to_silver.py` (`SilverMergeJobSpec`)
- `docs/specifications/data-contracts.md` and `models/domain/`

## 4. Preconditions

1. Target directory `README.md` has been read in full.
2. Target Medallion layer (`Bronze` or `Silver`), table owner, natural key, version column, event-time semantics, and recovery plan have been confirmed.

## 5. Execution Procedure

1. Define Iceberg catalog/namespace/table ownership and schema with explicit `Decimal` precision, nullability, units, and UTC semantics.
2. Keep Bronze append-only and source-preserving in MinIO (`Parquet`), recording `event_id`, `schema_version`, `ingested_at`, and source partition/offset metadata.
3. Use deterministic file/object naming so retry and offset-commit crash windows remain idempotent.
4. Configure Parquet compression (`ZSTD` / `Snappy`), target file size, and partition transforms without high-cardinality partition explosion.
5. Implement Silver typing, UTC normalization, and deterministic deduplication via PySpark Iceberg `MERGE INTO` (`SilverMergeJobSpec` in `src/processing/spark/bronze_to_silver.py`).
6. Integrate data quality checks (`QualityExpectationRule`) before promoting Silver tables.
7. Implement bounded backfill, checkpointing, compaction, and snapshot maintenance with dry-run controls, then run `tools/validators/run_all.py`.

## 6. Output Artifacts

- Iceberg table definitions, Bronze writer updates (`src/consumers/lakehouse_bronze/`), PySpark `Bronze -> Silver` jobs (`src/processing/spark/`), updated domain models (`models/domain/`), and lakehouse runbooks.

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

