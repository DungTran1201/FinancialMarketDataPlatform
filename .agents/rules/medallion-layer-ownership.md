# Data Rule — Medallion Layer Ownership (`DATA-RULE-006`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-006` |
| **Rule Slug** | `medallion-layer-ownership` |
| **Trigger Scope** | Bronze/Silver/Gold data, MinIO, Parquet, Iceberg, PySpark, dbt, and analytical marts |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Enforces strict responsibility boundaries across the Lakehouse Medallion layers (Bronze append-only raw archive, Silver PySpark Iceberg standardization/deduplication, and Gold dbt Core semantic marts) per `ADR-002` and `ADR-003`.

## 2. Mandatory Directives

1. **Immutable Bronze**: Keep Bronze append-only in MinIO (`Parquet`), preserving raw source payloads, `event_id`, `schema_version`, and ingestion lineage.
2. **PySpark-Owned Silver**: Use PySpark (`src/processing/spark/bronze_to_silver.py`) exclusively for Bronze-to-Silver type standardization, UTC normalization, and deterministic deduplication via Iceberg `MERGE INTO`.
3. **dbt-Owned Gold**: Keep curated business/analytical aggregations and marts in `dbt Core` (`src/transformation/dbt/`), avoiding duplicate business logic across Spark and dbt.
4. **Table Maintenance**: Govern Parquet file sizing, partition evolution, compaction, and Iceberg snapshot retention explicitly.

## 3. Prohibited Actions

- Do not mutate or overwrite Bronze into a cleaned business table.
- Do not implement Gold business metrics in PySpark when owned by dbt Core.
- Do not treat raw object-store Parquet paths as a substitute for transactional Apache Iceberg table metadata.

## 4. Verification Mechanism

- Model lineage inspection, `SilverMergeJobSpec` verification, dbt DAG/tests, and `tools/validators/run_all.py`.

