# Data Rule — Storage Workload Separation (`DATA-RULE-012`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-012` |
| **Rule Slug** | `storage-workload-separation` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Enforces strict polyglot storage workload separation across Redis (sub-15ms hot latest state), ClickHouse (real-time and historical OLAP aggregations), MinIO + Parquet + Apache Iceberg (immutable Bronze archive and deduplicated Silver/Gold lakehouse), and PostgreSQL 16 (transactional control plane, IAM, watermarks, and Agent state) per `docs/data-plane/architecture/data-storage-architecture.md` and `docs/overview/three-plane-architecture.md`.

## 2. Mandatory Directives

1. **Hot Path Isolation**: Serve sub-15ms latest price, 24h snapshot, and top-20 order book queries from Redis (`consumer-hot-redis`) with transparent fallback to ClickHouse on cache miss (`docs/application-plane/domains/market-experience-and-catalog/capabilities/market-and-analytics-query-portal/`).
2. **OLAP vs. OLTP Separation**: Keep high-throughput time-series and OHLCV queries in ClickHouse (`ReplacingMergeTree` / `AggregatingMergeTree`) and keep transactional control-plane records (users, RBAC, API keys, watermarks, job runs) in PostgreSQL 16.
3. **Lakehouse Medallion Boundaries**: Persist immutable raw event batches to MinIO Bronze (`Parquet`), run PySpark for Bronze-to-Silver Iceberg standardization/deduplication, and run dbt Core for Silver-to-Gold analytical marts (`docs/data-plane/domains/lakehouse-analytics/`).
4. **Evidence & Verification**: Run `scripts/docs/validate_docs.py` (`tools/validators/run_all.py`) and architectural boundary tests after modifying any storage contract or schema.

## 3. Prohibited Actions

- Never use ClickHouse or MinIO/Iceberg for transactional control-plane mutations or user/RBAC state.
- Never use PostgreSQL or Redis as a high-volume raw market tick or historical candle archive.
- Never issue unbounded full-table scans from online API or Agent Tool Gateway handlers.

## 4. Verification Mechanism

- Automated check via `scripts/docs/validate_docs.py` (`tools/validators/run_all.py`), `tests/architecture/test_clean_architecture_boundaries.py`, and `QG-3-SPEC-DESIGN` / `QG-6-VERIFY` review.
