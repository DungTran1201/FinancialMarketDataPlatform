# ADR-005: High-Performance Query Routing & Tiered Caching Strategy

- **Status**: Accepted
- **Date**: 2026-11-12
- **Deciders**: Backend & Data Platform Architecture Team

---

## 1. Decision Title

Implement **Workload-Classified Query Routing**, **Push-Updated Hot State in Redis** with monotonic timestamp protection, **Selective Cache-Aside with Stampede Protection** for expensive analytical aggregations, and **Graceful ClickHouse Fallback** on Redis unavailability.

---

## 2. Context

Clients and AI Agents issue queries with vastly different latency, freshness, and computational profiles:
- Polling latest prices and 24h market snapshots multiple times per second.
- Fetching historical OHLCV candles and trade ticks across arbitrary time windows.
- Computing rolling volatility, return distributions, and cross-asset correlation matrices.
- Inspecting long-term raw archival datasets.

---

## 3. Problem Statement

How do we achieve sub-15ms P95 latency on hot market endpoints and sub-200ms P95 latency on analytical queries while preventing cache stampedes, stale out-of-order overwrites, unbounded ClickHouse scans, and total system outage if Redis fails?

---

## 4. Selected Option

### 4.1. Explicit Query Classification & Routing Matrix
Every query is routed to the storage engine optimized for its access pattern:
1. **Latest Price & Market Snapshot** $\rightarrow$ **Redis Hot State** (populated continuously by `consumer-hot-redis`).
2. **Historical Candles & Trades** $\rightarrow$ **ClickHouse Base Tables** (`market_klines`, `market_trades`) using primary key prefix `(provider, symbol, interval, open_time)`.
3. **Rolling Market Statistics & OHLCV Rollups** $\rightarrow$ **ClickHouse Materialized Views** (`mv_klines_1h`, `mv_klines_1d`, `mv_symbol_stats_hourly`) with short-TTL Redis Cache-Aside ($15\text{ s}$).
4. **Control Metadata & Agent Run State** $\rightarrow$ **PostgreSQL**.
5. **Raw Historical Replay / Bulk Export** $\rightarrow$ **MinIO / Apache Iceberg** (asynchronous job only).

### 4.2. Redis Hot State & Monotonic Update Strategy
- **Key Namespace Convention**:
  - `market:v1:price:{provider}:{symbol}` (Hash: `last_price`, `exchange_event_time_ms`, `ingested_at_ms`) — TTL `300s`.
  - `market:v1:snapshot:{provider}:{symbol}` (Hash/JSON: 24h ticker + best bid/ask + spread) — TTL `300s`.
  - `market:v1:orderbook:{provider}:{symbol}` (JSON: top-20 bids/asks + `last_update_id`) — TTL `120s`.
  - `cache:v1:analytics:{query_hash}` (JSON: cached analytical aggregation) — TTL `15s - 60s`.
- **Out-of-Order Protection (Atomic Lua Script)**:
  - The Hot Cache Updater executes an atomic Redis Lua script that compares incoming `exchange_event_time_ms` (or `last_update_id`) against the currently stored value and **rejects the update if the incoming event is older than the stored state**.

### 4.3. Cache Stampede Protection & Graceful Fallback
- **Single-Flight / Lock Lease on Analytical Cache Miss**: When a popular analytical query (`cache:v1:analytics:{hash}`) misses or nears expiration, a short Redis lock (`lock:cache:{hash}`, TTL `3s`) ensures only one coroutine recomputes the ClickHouse query while concurrent requests either wait briefly or read slightly stale data.
- **Transparent ClickHouse Fallback**: If Redis throws a connection error or returns a cache miss on `/market/prices/{symbol}`, the `MarketQueryService` transparently falls back to a bounded ClickHouse query (`SELECT ... FROM market_tickers WHERE provider = ... AND symbol = ... ORDER BY exchange_event_time DESC LIMIT 1`), sets `meta.source = "clickhouse_fallback"`, and applies an in-memory circuit breaker / rate limiter so fallback traffic cannot overwhelm ClickHouse.

---

## 5. Alternative Options Considered

### Alternative A: Cache Every API Response Indiscriminately in Redis (HTTP Response Caching Middleware)
- **Rejection Reason**: Violates Section 7.2 ("Do not cache every API response indiscriminately"). Arbitrary historical time-range queries (`?start_time=X&end_time=Y`) have low cache hit ratios, pollute Redis memory, and evict critical hot market state.

### Alternative B: Serve All Queries Directly from ClickHouse Without Redis
- **Rejection Reason**: Violates Objective O1 and Section 7.1. High-concurrency polling of latest prices and snapshots across hundreds of connected dashboard/WebSocket clients would generate thousands of small point queries per second against ClickHouse, degrading its batch insert merging and analytical scan performance.

### Alternative C: Fail Hard (`HTTP 500/503`) When Redis Is Unavailable
- **Rejection Reason**: Violates Section 9.7 ("The system must remain functional when Redis becomes unavailable, using an appropriate fallback path").

---

## 6. Decision Rationale

Combining **push-based hot state** (for latest prices/snapshots) with **pull-based cache-aside** (only for repeatable analytical aggregations) and **direct ClickHouse partition-pruned scans** (for historical time-series ranges) maximizes cache hit rates while keeping Redis memory footprint tiny and deterministic.

---

## 7. Benefits

- **Sub-15ms Hot Reads**: Redis serves latest prices and snapshots in $<5\text{ ms}$ P50 without touching disk.
- **Zero Out-of-Order Regression**: Atomic Lua timestamp comparison prevents delayed Kafka retries from overwriting newer prices in Redis.
- **High Resilience**: Redis restarts or evictions degrade latency gracefully (to $\sim 25\text{ ms}$ via ClickHouse fallback) rather than causing service downtime.

---

## 8. Drawbacks

- Requires maintaining Lua scripts and fallback adapters in the Market infrastructure layer.
- Stale data detection requires comparing `exchange_event_time_ms` against current UTC wall clock on every read (`is_stale = (now - exchange_event_time) > staleness_threshold`).

---

## 9. Architectural Limitations

- Redis does not store historical time series; any request for historical candles or trade history bypasses Redis and queries ClickHouse directly.
- ClickHouse fallback cannot sustain the same infinite point-lookup QPS as Redis; therefore, fallback mode enforces a stricter rate limit (`30 req/s` global fallback budget) to protect ClickHouse stability.

---

## 10. Operational Implications

- Configure Redis with `maxmemory 256mb` and `maxmemory-policy volatile-lru` so keys with shorter TTLs (`cache:v1:analytics:*`) are evicted before hot market state keys, and never persist historical logs in Redis.
- Expose Prometheus metrics `redis_cache_hit_total`, `redis_cache_miss_total`, `market_stale_read_total`, and `market_clickhouse_fallback_total`.

---

## 11. Consequences

- All hot responses include `meta.as_of` (`exchange_event_time`), `meta.age_ms`, `meta.is_stale`, and `meta.source` (`redis_hot_cache` or `clickhouse_fallback`) so API consumers and AI Agents always know exact data freshness.

---

## 12. Conditions That Could Invalidate This Decision

1. If historical candle queries for identical canonical windows (e.g., "last 100 `1m` candles for `BTCUSDT`") become heavily repeated by thousands of anonymous users, a short-TTL ($2\text{ s}$) edge/Redis cache specifically for canonical head windows can be enabled.

