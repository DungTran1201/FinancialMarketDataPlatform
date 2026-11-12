# Diagram 11: Cache Architecture (Hot Push, Analytical Cache-Aside & Stampede Protection)

## Architectural Explanation

The **Cache Architecture Diagram** defines the two distinct caching patterns implemented in Redis and their failure/invalidation guarantees:

1. **Pattern 1 — Push-Driven Hot State (`market:v1:*`)**:
   - Populated continuously by `consumer-hot-redis` from Kafka.
   - Uses an **Atomic Lua Script** that checks `if tonumber(ARGV[1]) >= tonumber(current_event_time) then HSET ... EXPIRE 300 end` to guarantee out-of-order Kafka retries never overwrite newer market prices.
   - On cache miss or Redis outage, `MarketQueryService` falls back to ClickHouse via a rate-limited circuit breaker.
2. **Pattern 2 — Pull-Driven Analytical Cache-Aside with Stampede Lock (`cache:v1:analytics:*`)**:
   - Used only for repeatable expensive analytical aggregations (e.g., 24h rolling volatility summary, multi-symbol correlation matrix) with short TTLs ($15\text{ s} - 60\text{ s}$).
   - **Stampede Protection**: On a cache miss, the first request acquires a short distributed lease (`SET lock:cache:{hash} 1 NX PX 3000`), queries ClickHouse Materialized Views, populates Redis, and releases the lock while concurrent callers wait briefly for the populated cache entry.

```mermaid
flowchart TB
    subgraph PushPath["Pattern 1: Push-Driven Hot Market State (market:v1:*)"]
        KafkaHot["Kafka: trades / tickers / klines / orderbook"]
        HotConsumer["consumer-hot-redis"]
        LuaGuard["Atomic Redis Lua Script<br/>Check: incoming_event_ts >= stored_event_ts"]
        HotKeys[("Redis Hot Namespace<br/>market:v1:price:{provider}:{symbol} (TTL 300s)<br/>market:v1:snapshot:{provider}:{symbol} (TTL 300s)<br/>market:v1:orderbook:{provider}:{symbol} (TTL 120s)")]

        KafkaHot --> HotConsumer --> LuaGuard
        LuaGuard -->|"Newer Event: Update & Reset TTL"| HotKeys
        LuaGuard -.->|"Older Event: Drop & Increment Metric"| Ignored["Out-of-Order Counter"]
    end

    subgraph PullPath["Pattern 2: Analytical Cache-Aside + Stampede Lock (cache:v1:analytics:*)"]
        APIReq["FastAPI AnalyticsQueryService"]
        AnalyticKeys[("Redis Cache Namespace<br/>cache:v1:analytics:{query_hash} (TTL 15-60s)")]
        StampedeLock["Redis Distributed Lease<br/>SET lock:cache:{hash} NX PX 3000"]
        CHQuery[("ClickHouse OLAP / Materialized Views")]

        APIReq -->|"1. Check Cache"| AnalyticKeys
        AnalyticKeys -.->|"2. Cache Miss"| StampedeLock
        StampedeLock -->|"3a. Lock Acquired (Leader)"| CHQuery
        CHQuery -->|"4. Write Result with TTL"| AnalyticKeys
        StampedeLock -.->|"3b. Lock Held (Follower)"| WaitPoll["Wait 50ms & Read Populated Key"]
        WaitPoll --> AnalyticKeys
    end

    subgraph FallbackPath["Resilience: Redis Miss / Outage Fallback"]
        MarketAPI["FastAPI MarketQueryService"]
        CircuitBreaker["Fallback Circuit Breaker & Rate Limiter<br/>(Max 30 req/s to Protect ClickHouse)"]

        MarketAPI -->|"Read Hot State"| HotKeys
        HotKeys -.->|"Miss or Redis Down"| CircuitBreaker
        CircuitBreaker -->|"Bounded Point Lookup"| CHQuery
    end
```

