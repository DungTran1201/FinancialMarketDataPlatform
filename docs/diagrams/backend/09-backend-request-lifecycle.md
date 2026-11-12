# Diagram 09: Backend Request Lifecycle (Synchronous Hot/OLAP Read vs. Asynchronous Job)

## Architectural Explanation

The **Backend Request Lifecycle Sequence Diagram** contrasts two fundamental execution paths in the FastAPI backend:
1. **Path A — Low-Latency Synchronous Read (`GET /api/v1/market/prices/BTCUSDT`)**:
   - Passes through Correlation ID middleware, JWT/API-Key authentication, and Redis sliding-window rate limiting.
   - `MarketQueryHandler` queries `RedisMarketHotAdapter` ($<5\text{ ms}$).
   - If Redis misses or is unreachable, transparently falls back to `ClickHouseMarketAdapter` with circuit-breaker protection, computes staleness metadata (`is_stale`), and returns `200 OK`.
2. **Path B — Long-Running Asynchronous Job (`POST /api/v1/agents/runs` or Heavy Backfill)**:
   - Validates request schema and `Idempotency-Key`, persists a `QUEUED` run record in PostgreSQL, notifies the background worker queue, and immediately returns `202 Accepted` with `run_id` and status polling / SSE URLs so the FastAPI event loop is never blocked.

```mermaid
sequenceDiagram
    autonumber
    actor Client as API Client
    participant API as FastAPI Router & Middleware
    participant Auth as Auth & RateLimiter (Redis)
    participant Handler as Application Query/Command Handler
    participant Redis as Redis Hot Store
    participant CH as ClickHouse OLAP
    participant PG as PostgreSQL Control DB
    participant Worker as Async Agent / Batch Worker

    rect rgb(235, 248, 255)
        Note over Client,CH: Path A: Synchronous Low-Latency Market Read (GET /api/v1/market/prices/BTCUSDT)
        Client->>API: GET /api/v1/market/prices/BTCUSDT (Bearer JWT)
        API->>Auth: Validate JWT & Check Rate Limit (120 req/min)
        Auth-->>API: Authorized (role=viewer)
        API->>Handler: Execute GetLatestPriceQuery(provider="binance", symbol="BTCUSDT")
        Handler->>Redis: HGETALL market:v1:price:binance:BTCUSDT
        alt Cache Hit & Fresh
            Redis-->>Handler: {last_price, exchange_event_time_ms}
            Handler-->>API: PriceDTO(source="redis_hot_cache", is_stale=false)
        else Cache Miss or Redis Down
            Redis-->>Handler: Miss / ConnectionError
            Handler->>CH: SELECT argMax(last_price, exchange_event_time) FROM market_tickers WHERE symbol='BTCUSDT'
            CH-->>Handler: Fallback Price Row
            Handler-->>API: PriceDTO(source="clickhouse_fallback", is_stale=...)
        end
        API-->>Client: 200 OK (Standard JSON Envelope + Request-ID)
    end

    rect rgb(255, 245, 235)
        Note over Client,Worker: Path B: Asynchronous Expensive Workflow (POST /api/v1/agents/runs)
        Client->>API: POST /api/v1/agents/runs (Idempotency-Key, Prompt/Symbol)
        API->>Auth: Validate JWT (role>=analyst) & Rate Limit (5 req/min)
        Auth-->>API: Authorized
        API->>Handler: Execute CreateAgentRunCommand
        Handler->>PG: INSERT INTO agent_runs (run_id, status='QUEUED', ...)
        PG-->>Handler: Committed run_id
        Handler->>Redis: LPUSH / PUBLISH agent:jobs:queue {run_id}
        Handler-->>API: RunAcceptedDTO(run_id, status="QUEUED")
        API-->>Client: 202 Accepted (Location: /api/v1/agents/runs/{run_id})
        Redis->>Worker: Dequeue {run_id}
        Worker->>PG: UPDATE agent_runs SET status='RUNNING'
        Worker->>CH: Execute Deterministic Quant Tools
        Worker->>PG: UPDATE agent_runs SET status='COMPLETED', structured_report=...
    end
```

