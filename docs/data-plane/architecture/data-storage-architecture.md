---
doc_id: DP-ARCH-STOR-001
title: "Data Plane Polyglot Storage Architecture"
doc_type: architecture
plane: data-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/streaming/consumers/hot_redis.py"
    - "src/streaming/consumers/analytics_ch.py"
    - "src/ingestion/infrastructure/watermark_store.py"
    - "src/lakehouse/silver/merge_engine.py"
    - "deploy/clickhouse/init/01_schema.sql"
    - "deploy/iceberg/catalog-config.yaml"
related_docs:
  - DP-ARCH-001
  - DP-ROOT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Separated AS-IS Python/SQLite/local-disk storage from TARGET Redis, ClickHouse, Postgres, MinIO, and Iceberg DDL."
---

# Data Plane Polyglot Storage Architecture

## 1. Storage Tiers Scope & Workload Separation `[REQUIRED]`

FMDP isolates workloads across four storage roles to prevent analytical batch scans from starving millisecond hot market reads or control-plane state updates.

## 2. Context & Configured Storage Engines `[REQUIRED]`

- `deploy/clickhouse/init/01_schema.sql` (`market_data` DB, `Decimal128(18)`), `deploy/postgres/init/01_schema.sql` (`fmdp_control` DB), `docker-compose.yml` (`redis:7.2-alpine`, `kafka:3.7.0`, `minio`), `deploy/iceberg/catalog-config.yaml` (`fmdp_iceberg`).

## 3. Building Block Comparison: `AS-IS` Reality vs. `TARGET` Infrastructure `[REQUIRED]`

| Tier | Workload | `AS-IS` Physical Mechanism | `TARGET` Infrastructure & Schema | Verified Inconsistencies (`7880c85`) |
|---|---|---|---|---|
| **Hot Serving Cache** | Sub-second latest quote, 24h snapshot, depth-20 | Python dicts (`_price_store`, `_snapshot_store`, `_orderbook_store`) + optional JSON dump | Redis 7 (`256mb`, `volatile-lru`), monotonic Lua `REDIS_MONOTONIC_UPSERT_LUA`, TTL `300s`/`120s` | `_redis_client=None` in runtime; `_sync_record_to_live_redis` skips snapshot/orderbook keys and writes `last_price="0"` on price-less depth frames. |
| **Streaming Analytical OLAP** | Micro-batched historical klines, trades, VWAP/volatility | Python dicts (`_trades_table`, `_klines_table`, `_tickers_table`) + klines-only JSON persistence | ClickHouse 24.3 `ReplacingMergeTree` (`market_trades`, `market_klines`, `market_tickers`) | `_clickhouse_client` unused; **0 Materialized Views** in `01_schema.sql`; snapshot table names (`*_raw`, `*_1m`, `*_latest`) differ from SQL DDL; flush uses row count `5000` only (`flush_interval_ms` unimplemented). |
| **Control Watermarks** | Per-symbol backfill resume boundary | SQLite WAL file `.local_storage/control_watermarks.db` (`ingestion_watermarks`) | PostgreSQL 16 `ingestion_watermarks` table | SQLite columns (`provider, symbol, interval, last_open_time, updated_at, status`) & enum (`SYNCED|BACKFILLING|GAP_DETECTED`) mismatch Postgres (`watermark_id, dataset, last_synced_timestamp, IDLE|RUNNING|FAILED|COMPLETED`). |
| **Medallion Lakehouse** | Immutable Bronze raw, deduplicated Silver, Gold `Decimal` marts | Local `.local_lakehouse/` atomic ZSTD Parquet + hand-rolled JSON `v{id}.metadata.json` (`max_snapshots_to_keep=5`) | MinIO S3 (`lakehouse-bronze/silver/gold`), PySpark/PyIceberg REST (`:8181`), dbt incremental marts | No `iceberg-rest` container in Compose; `MINIO_ENDPOINT` vs `MINIO_ENDPOINT_URL` mismatch; `init-buckets.sh` vs `LAKEHOUSE_BUCKET=market-data` conflict; `fct_daily_market_summary.sql` is the only dbt SQL model; Silver `_IO_LOCK` excludes metadata JSON writes. |

## 4. Storage Precision & Immutability Rules

- **ClickHouse Precision**: `Decimal128(18)` for prices/quantities, `Decimal64(6)` for percentage change, `DateTime64(3, 'UTC')` timestamps.
- **Silver Deduplication**: Natural-key upserts (`provider, symbol, interval, open_time` for klines; `provider, symbol, trade_id` for trades) quantized to `Decimal("0.00000001")`.
