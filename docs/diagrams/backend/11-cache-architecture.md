# Diagram 11: Cache Architecture (Hot Push, Analytical Cache-Aside & Stampede Protection) (`DIAG-COMP-011`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-COMP-011` |
| **Title** | Cache Architecture (Hot Push & Planned Stampede Protection) |
| **Diagram Category** | `docs/diagrams/backend/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart TB)` |
| **Status** | `PARTIALLY_IMPLEMENTED` (Pattern 1 Hot State & ClickHouse fallback `[IMPLEMENTED]`; Pattern 2 `lock:cache:{hash}` stampede keys `[PLANNED]`) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/05-backend-architecture.md`, `docs/architecture/13-performance-and-scalability.md` |
| **Canonical Model Reference** | `models/architecture/components.yaml`, `models/requirements/requirements.yaml` |
| **Related Artifact IDs** | `BR-003`, `AC-002`, `NFR-001`, `TC-002`, `TC-007` |

## Architectural Explanation

The **Cache Architecture Diagram** distinguishes active Redis hot-path projection from the planned analytical stampede-protection pattern:

1. **Pattern 1 — Push-Driven Hot State (`market:v1:*`, `[IMPLEMENTED]`)**:
   - Populated by `HotStateProjector` (`cg.hot.redis.v1`) with monotonic timestamp enforcement (`BR-003`: atomic Lua check `if tonumber(ARGV[1]) >= tonumber(current_event_time) then ... end`, dropping out-of-order stale events and incrementing `fmdp_hot_out_of_order_dropped_total`).
   - On cache miss or Redis unavailability, `GetLatestPriceHandler` falls back to ClickHouse (`AC-002`).
2. **Pattern 2 — Pull-Driven Analytical Cache-Aside with Stampede Lock (`cache:v1:analytics:*`, `[PLANNED / DESIGNED PATTERN]`)**:
   - Designed target for repeatable expensive analytical aggregations using short distributed leases (`SET lock:cache:{hash} 1 NX PX 3000`); not yet wired into active analytics routers (see `13-performance-and-scalability.md`).

```mermaid
flowchart TB
    subgraph PushPath["Pattern 1: Push-Driven Hot Market State [IMPLEMENTED]"]
        KafkaHot["Kafka: trades / tickers / klines / orderbook"]
        HotConsumer["HotStateProjector (cg.hot.redis.v1)"]
        LuaGuard["Monotonic Timestamp Guard (BR-003)<br/>Check: incoming_event_ts >= stored_event_ts"]
        HotKeys[("Redis Hot Namespace<br/>market:v1:price:{provider}:{symbol} (TTL 300s)<br/>market:v1:snapshot:{provider}:{symbol} (TTL 300s)<br/>market:v1:orderbook:{provider}:{symbol} (TTL 120s)")]

        KafkaHot --> HotConsumer --> LuaGuard
        LuaGuard -->|"Newer Event: Update & Reset TTL"| HotKeys
        LuaGuard -.->|"Older Event: Drop & fmdp_hot_out_of_order_dropped_total"| Ignored["Out-of-Order Counter"]
    end

    subgraph PullPath["Pattern 2: Analytical Cache-Aside + Stampede Lock [PLANNED TARGET]"]
        APIReq["FastAPI AnalyticsQueryService"]
        AnalyticKeys[("Planned Key: cache:v1:analytics:{hash} (TTL 15-60s)")]
        StampedeLock["Planned Lease: SET lock:cache:{hash} NX PX 3000"]
        CHQuery[("ClickHouse OLAP / Materialized Views")]

        APIReq -->|"1. Check Cache [PLANNED]"| AnalyticKeys
        AnalyticKeys -.->|"2. Cache Miss"| StampedeLock
        StampedeLock -.->|"3a. Lock Acquired (Leader)"| CHQuery
        CHQuery -.->|"4. Write Result with TTL"| AnalyticKeys
        StampedeLock -.->|"3b. Lock Held (Follower)"| WaitPoll["Wait 50ms & Read Key"]
        WaitPoll -.-> AnalyticKeys
    end

    subgraph FallbackPath["Resilience: Redis Miss / Outage Fallback [IMPLEMENTED]"]
        MarketAPI["FastAPI GetLatestPriceHandler"]
        CircuitBreaker["ClickHouse OLAP Fallback Handler<br/>(Fallback Alert & Source Tagging AC-002)"]

        MarketAPI -->|"Read Hot State"| HotKeys
        HotKeys -.->|"Miss or Redis Down"| CircuitBreaker
        CircuitBreaker -->|"OLAP Point Lookup"| CHQuery
    end
```

