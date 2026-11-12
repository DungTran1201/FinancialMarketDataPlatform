# 13 — Performance and Scalability Architecture

## 1. High-Performance Design Philosophy

Performance is enforced structurally through **workload classification**, **storage specialization**, **micro-batched columnar writes**, **push-updated hot caching**, and **asynchronous execution boundaries**, rather than ad-hoc late-stage tuning.

See also:
- [Non-Functional Requirements Specification](../specifications/non-functional-requirements.md)
- [ADR-005: Query and Caching Strategy](adr/ADR-005-query-and-caching-strategy.md)
- [Diagram 11: Cache Architecture](../diagrams/backend/11-cache-architecture.md)

---

## 2. Complete Query Classification & Routing Matrix

In accordance with Section `7.1`, no single database serves all query types:

| Query Category | Storage Source | Access Pattern | Expected Frequency | Freshness Target | Query Complexity | Cache Strategy | Failure Behavior |
|---|---|---|---|---|---|---|---|
| **1. Latest Price** | **Redis** (`Fallback: CH`) | Point lookup by `market:v1:price:{provider}:{symbol}` | Very High ($50-500\text{ req/s}$) | $\le 500\text{ ms}$ | $O(1)$ key lookup | Push-updated by `consumer-hot-redis` (TTL `300s`) | Transparent fallback to ClickHouse `argMax` with rate limit (`30 req/s`). |
| **2. Market Snapshot** | **Redis** (`Fallback: CH`) | Point lookup by `market:v1:snapshot:{provider}:{symbol}` | High ($20-200\text{ req/s}$) | $\le 1\text{ s}$ | $O(1)$ hash/JSON read | Push-updated by `consumer-hot-redis` (TTL `300s`) | Transparent fallback to ClickHouse latest ticker + book query. |
| **3. Historical Candles** | **ClickHouse** (`market_klines`) | Bounded range scan on `(provider, symbol, interval, open_time)` | Medium ($10-50\text{ req/s}$) | $1-5\text{ s}$ | $O(\log N + K)$ granule scan ($K \le 1000$) | Direct ClickHouse scan (OS page cache + uncompressed block cache) | Returns `HTTP 503` with `Retry-After: 5` if ClickHouse is unreachable. |
| **4. Historical Trades** | **ClickHouse** (`market_trades`) | Bounded range scan on `(provider, symbol, trade_time)` | Low–Medium ($5-20\text{ req/s}$) | $1-5\text{ s}$ | $O(\log N + K)$ granule scan ($K \le 500$) | Direct ClickHouse scan; no Redis caching of tick ranges | Returns `HTTP 503` if ClickHouse is unreachable. |
| **5. Market Statistics** | **ClickHouse** (`market_tickers` / `mv_*`) | Bounded aggregation over `1h`, `24h`, `7d`, `30d` window | Medium ($10-40\text{ req/s}$) | $5-15\text{ s}$ | Pre-aggregated MV scan | Redis Cache-Aside (`cache:v1:analytics:*`, TTL `15s`) + Stampede lock | Serves directly from ClickHouse MV if Redis is down. |
| **6. Aggregated Analytics (Volatility / Correlation)** | **ClickHouse Materialized Views & Base** | Multi-symbol time-series join / array aggregation | Low ($1-10\text{ req/s}$) | $15-60\text{ s}$ | Medium column scan ($\le 90\text{ days}$) | Redis Cache-Aside (`TTL 60s`) with single-flight stampede lock | Offloads windows $>90\text{ days}$ to asynchronous analytics job queue. |
| **7. User & Platform Configuration** | **PostgreSQL** (`monitored_instruments`, `users`) | Primary key / indexed lookup | Low–Medium ($5-30\text{ req/s}$) | Immediate ACID | $O(\log N)$ B-Tree index lookup | Instrument list cached in-memory/Redis (`TTL 60s`), invalidated on `PUT` | Direct PostgreSQL read; fails closed (`HTTP 503`) for auth writes if PG is down. |
| **8. Agent Execution State** | **PostgreSQL** (`agent_runs`, `agent_tool_invocations`) | Primary key lookup by `run_id` | Low ($1-10\text{ req/s}$) | Immediate ACID | $O(\log N)$ PK lookup | No cache for active `RUNNING` state; `COMPLETED` reports cached (`TTL 300s`) | Returns `HTTP 503` on `/api/v1/agents/*`; zero impact on Market/Analytics APIs. |
| **9. Historical Raw Data** | **MinIO / Apache Iceberg** (`bronze.*`, `silver.*`) | Batch partition scan by `(provider, date)` | Batch / Scheduled only | $5-60\text{ m}$ | Large sequential columnar scan | Never queried synchronously by REST API | Retried by Airflow / PySpark job runner. |

---

## 3. Caching Architecture Details

1. **Key Naming Convention**:
   - Hot Price: `market:v1:price:{provider}:{symbol}`
   - Hot Snapshot: `market:v1:snapshot:{provider}:{symbol}`
   - Hot Order Book: `market:v1:orderbook:{provider}:{symbol}`
   - Analytical Cache-Aside: `cache:v1:analytics:{endpoint}:{sha256_canonical_params}`
   - Stampede Lease Lock: `lock:v1:cache:{sha256_canonical_params}`
   - Rate Limit Counter: `ratelimit:v1:{scope}:{identifier}:{minute_bucket}`
2. **Cache Stampede Protection**:
   - Analytical Cache-Aside uses a distributed Redis lock (`SET lock:v1:cache:{hash} 1 NX PX 3000`). Only the lock holder queries ClickHouse and populates the cache key; concurrent requests wait up to `150ms` for the key to appear before falling back.
3. **Stale Data Policy**:
   - Every cached market payload embeds `exchange_event_time_ms` and `ingested_at_ms`.
   - On read, the application calculates `age_ms = now_utc_ms - exchange_event_time_ms`. If `age_ms > 15,000`, the API response sets `meta.is_stale = true` so callers never mistake a frozen price during an exchange outage for a live tick.

---

## 4. Database & Event Loop Performance Isolation

1. **ClickHouse Micro-Batching**:
   - ClickHouse performance degrades severely if clients issue hundreds of individual row inserts per second (`Too many parts`). `consumer-analytics-ch` enforces strict micro-batching (`flush_interval = 1.0s` or `max_rows = 5,000`), writing only 1 part per second per table.
2. **Bounded Query Cost Guards**:
   - Every ClickHouse read connection from `backend-api` and `agent-worker` sets `max_execution_time = 5` (or `8` for correlation matrices), `max_rows_to_read = 500000`, and `readonly = 1`.
3. **FastAPI Event Loop Non-Blocking Rule**:
   - All I/O drivers in `backend-api` are asynchronous (`redis.asyncio`, `asyncpg`, async ClickHouse HTTP client).
   - CPU-bound tasks (Spark transformations, multi-step LangGraph reasoning, historical backfills) run in separate container processes (`spark-worker`, `agent-worker`, `collector-rest`).

