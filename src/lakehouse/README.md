# Lakehouse Subsystem (`src/lakehouse/`)

Owns **Stages 5–9 & Stage 12** of the Medallion Lakehouse (`Bronze -> Silver -> Gold`), blocking automated Data Quality gates, dataset catalog/lineage governance, and end-to-end Data Platform v0.1 orchestration.

## Subpackages

| Directory | Responsibility | Key Artifacts |
|---|---|---|
| `bronze/` | Immutable ZSTD-compressed Apache Parquet raw archive (`BronzeParquetArchiver`) and `consumer-lakehouse-bronze` worker entrypoint (`consumer.py`) | Partitioned `bronze/{event_type}/provider={p}/ingestion_date={YYYY-MM-DD}`. |
| `silver/` | Natural-key deduplicated `MERGE INTO` standardization, small-file Parquet compaction, and cumulative Apache Iceberg v2 snapshots (`SilverLakehouseMergeEngine`) | Compacts small files sorted by natural key (`files_after_compaction == 1`). |
| `gold/` | Fixed-point `Decimal` Gold analytical mart engine (`GoldLayerMartEngine`) and ClickHouse **dbt** project (`gold/dbt/`) | `fct_daily_market_summary`, `fct_realized_volatility`, `fct_orderbook_liquidity`. |
| `quality/` | Pre-Gold blocking expectations (`DataQualityGateEngine`: `DQ-KLINE-001..005`, `DQ-TRADE-*`) raising `QualityGateBlockedError` on `CRITICAL` failures | Prevents corrupt Silver rows from promoting to Gold. |
| `catalog/` | End-to-end dataset catalog & directed acyclic lineage graph (`DataLineageGovernanceRegistry`) | Tracks `Source -> Kafka -> Bronze -> Silver -> Gold -> Serving`. |
| `orchestration/` | `DataPlatformV01Pipeline` (`pipeline.py`) — end-to-end Data Plane composition root executing Stages 1–12 | Explicit orchestrator connecting `ingestion`, `streaming`, and `lakehouse`. |

