---
doc_id: CAP-DP-STR2-DB-001
title: "Physical Storage Design: Redis Keyspace & ClickHouse DDL"
doc_type: specification
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: database-architect
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "deploy/clickhouse/init/01_schema.sql"
    - "src/streaming/consumers/hot_redis.py"
    - "src/streaming/consumers/analytics_ch.py"
related_docs:
  - CAP-DP-STR2-MOD-001
  - DIAG-DP-STR2-ERD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Documented exact ClickHouse 01_schema.sql DDL (0 MVs), Redis volatile-lru config, and simulation dict gaps."
---

# Physical Storage Design: Redis Keyspace & ClickHouse DDL

Derived ERD: [olap-erd.md](olap-erd.md) (`DIAG-DP-STR2-ERD-001`).

## 1. ClickHouse Physical Schema (`deploy/clickhouse/init/01_schema.sql`, `market_data`) `[REQUIRED]`

| Table | Engine & Version Column | Partition & Order By | TTL & Granularity |
|---|---|---|---|
| `market_data.market_trades` | `ReplacingMergeTree(ingested_at)` | `PARTITION BY toYYYYMM(trade_time)`, `ORDER BY (provider, symbol, trade_time, trade_id)` | `90 DAY` (`trade_time`), `8192` |
| `market_data.market_klines` | `ReplacingMergeTree(exchange_event_time)` | `PARTITION BY toYYYYMM(open_time)`, `ORDER BY (provider, symbol, interval, open_time)` | No TTL, `8192` |
| `market_data.market_tickers` | `ReplacingMergeTree(exchange_event_time)` | `PARTITION BY toYYYYMM(exchange_event_time)`, `ORDER BY (provider, symbol, exchange_event_time)` | `90 DAY` (`exchange_event_time`), `8192` |

- **Materialized Views Reality**: `01_schema.sql` defines **0** Materialized Views (though analytics responses tag `meta.source = "clickhouse_mv_rollup"`). `ClickHouseBatchSink` runs via in-memory Python dicts (`_trades_table`, `_klines_table`, `_tickers_table`) with table labels `market_trades_raw`, `market_klines_1m`, `market_tickers_latest` in snapshot output.

## 2. Redis Physical Design & Migration Caveats `[REQUIRED]`

- Compose runs `redis:7.2-alpine` with `--maxmemory 256mb --maxmemory-policy volatile-lru --save "" --appendonly no` (`docker-compose.yml:47`).
- Lua `REDIS_MONOTONIC_UPSERT_LUA` (`hot_redis.py:20-31`) updates fields starting at `ARGV[3]` and applies `EXPIRE` (`ARGV[2]`), unused while `_redis_client=None`.
- **Migration / Rollback**: ClickHouse schema evolves additively via `ALTER TABLE ... ADD COLUMN`; `ReplacingMergeTree` merges asynchronously (`OPTIMIZE TABLE ... FINAL` or `FINAL` modifier required for strict deduplicated reads).
