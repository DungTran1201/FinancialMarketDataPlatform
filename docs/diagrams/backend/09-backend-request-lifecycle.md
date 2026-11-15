# Diagram 09: Backend Request Lifecycle (Synchronous Hot/OLAP Read vs. Asynchronous Job) (`DIAG-SEQ-009`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-SEQ-009` |
| **Title** | Backend Request Lifecycle Sequence Diagram |
| **Diagram Category** | `docs/diagrams/backend/` |
| **Notation / Mermaid Type** | `Mermaid (sequenceDiagram)` |
| **Status** | `IMPLEMENTED` / `PARTIALLY_IMPLEMENTED` (route RBAC `PROP-APP-004` & external Redis agent worker queue `[PLANNED]`) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/05-backend-architecture.md`, `docs/architecture/09-api-and-integration-architecture.md` |
| **Canonical Model Reference** | `models/interaction/interactions.yaml` |
| **Related Artifact IDs** | `API-001`, `API-008`, `AC-002`, `PROP-APP-004` |

## Architectural Explanation

The **Backend Request Lifecycle Sequence Diagram** contrasts two core execution paths in the FastAPI backend (`src/serving/api/main.py`):
1. **Path A — Low-Latency Synchronous Read (`GET /api/v1/market/prices/BTCUSDT`, `API-001`)**:
   - Passes through IAM defense middleware (`SlidingWindowRateLimiter` in-memory `120 req/min` default tier; note `[PROP-APP-004]`: route-level JWT/RBAC `Depends(...)` on non-IAM domain routers is `[PLANNED]`).
   - `GetLatestPriceHandler` queries `HotStateProjector` (Redis/in-memory hot state) and transparently falls back to `ClickHouseBatchSink` (`AC-002`) with staleness metadata (`is_stale`), returning `200 OK`.
2. **Path B — Agent Investigation Run (`POST /api/v1/agents/runs`, `API-008`)**:
   - Executes `runtime.execute_agent_investigation(...)` (`5-node MarketIntelligenceGraph` + `10-tool ControlledToolGateway`) and returns `202 Accepted` with `run_id`. Note: standalone Redis `LPUSH` job queue decoupling to an external `agent-worker` process is `[PARTIALLY_IMPLEMENTED / PLANNED]`.

```mermaid
sequenceDiagram
    autonumber
    actor Client as API Client
    participant API as FastAPI Router & Middleware
    participant Auth as SlidingWindowRateLimiter (In-Memory; RBAC PROP-APP-004 PLANNED)
    participant Handler as Application Query/Command Handler
    participant Redis as Redis / HotStateProjector
    participant CH as ClickHouse / OLAP Adapter
    participant Runtime as PlatformRuntimeContainer / State Store

    rect rgb(235, 248, 255)
        Note over Client,CH: Path A: Synchronous Market Read (GET /api/v1/market/prices/BTCUSDT)
        Client->>API: GET /api/v1/market/prices/BTCUSDT
        API->>Auth: Check Tier Rate Limit (120 req/min default; JWT guard PROP-APP-004 PLANNED)
        Auth-->>API: Allowed
        API->>Handler: Execute GetLatestPriceQuery(provider="binance", symbol="BTCUSDT")
        Handler->>Redis: Lookup hot price (market:v1:price:binance:BTCUSDT)
        alt Cache Hit & Fresh
            Redis-->>Handler: {last_price, exchange_event_time}
            Handler-->>API: PriceDTO(source="redis_hot_cache", is_stale=false)
        else Cache Miss or Redis Unavailable
            Redis-->>Handler: Miss / Unavailable
            Handler->>CH: Fallback OLAP query (market_tickers / sink)
            CH-->>Handler: Fallback Price Row
            Handler-->>API: PriceDTO(source="clickhouse_fallback", is_stale=...)
        end
        API-->>Client: 200 OK (Standard JSON Envelope {data, meta})
    end

    rect rgb(255, 245, 235)
        Note over Client,Runtime: Path B: Agent Investigation (POST /api/v1/agents/runs)
        Client->>API: POST /api/v1/agents/runs (Idempotency-Key, symbol, prompt_summary)
        API->>Auth: Check Analytics/Agent Rate Limit Tier (5 req/min)
        Auth-->>API: Allowed
        API->>Runtime: execute_agent_investigation(...) [In-Process; External PG/Redis Queue PLANNED]
        Runtime->>CH: Execute 5-Node Graph & 10 Deterministic Quant Tools
        Runtime-->>API: Ticket + MarketIntelligenceState (evidence_trail, status)
        API-->>Client: 202 Accepted ({data: {run_id, status, tool_calls_executed}, meta})
    end
```

