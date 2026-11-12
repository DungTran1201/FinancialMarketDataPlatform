# 09 — API and Integration Architecture

## 1. API Design Principles & Protocol Selection

The Backend Application Plane exposes three distinct client communication protocols, each matched to its interaction semantics:

| Protocol | Base Path | Use Case | Why Selected |
|---|---|---|---|
| **REST over HTTPS (JSON)** | `/api/v1/*` | Synchronous resource queries (latest prices, historical klines/trades, market stats, catalog CRUD) and asynchronous job submission (`202 Accepted`). | Cacheable, stateless, standard OpenAPI 3.1 contract, universal client support. |
| **WebSocket (WSS)** | `/ws/v1/market/stream` | Bidirectional live market streaming where clients dynamically subscribe/unsubscribe to symbol ticker and kline feeds. | Eliminates HTTP polling overhead; multiplexed over a single persistent TCP connection backed by Redis Pub/Sub. |
| **Server-Sent Events (SSE)** | `/api/v1/agents/runs/{run_id}/events` | Unidirectional progress notifications for active LangGraph Agent workflows (node transitions, tool executions, completion). | Standard HTTP/2 stream compatible with standard bearer auth and automatic client reconnection. |

### Strict Client Isolation Rule
- Browsers, desktop apps, and external API consumers **never** connect directly to Apache Kafka, Redis, ClickHouse, PostgreSQL, or MinIO. All external traffic terminates at `backend-api` (or `superset` for authenticated internal BI users).

---

## 2. API Domain Boundaries & Query Guardrails

See also: [API Specification](../specifications/api-specification.md) and [Diagram 09: Backend Request Lifecycle](../diagrams/backend/09-backend-request-lifecycle.md).

| API Domain | Prefix | Primary Storage Target | Max Page Size / Limit | Hard Timeout | Rate Limit (Per Key/User) | Idempotency Requirement |
|---|---|---|---|---|---|---|
| **Market API** | `/api/v1/market` | Redis (`Fallback: ClickHouse`) | `50` symbols batch | `1.5s - 2.0s` | `120 req/min` | Read-only (Safe) |
| **Historical Data API** | `/api/v1/historical` | ClickHouse (`Reads`), PostgreSQL (`Jobs`) | `1,000` klines / `500` trades | `5.0s` | `120 req/min` (`Reads`), `10 req/min` (`Backfill`) | `Idempotency-Key` required on `POST /backfill-jobs` |
| **Analytics API** | `/api/v1/analytics` | ClickHouse MV + Redis Cache-Aside | Max `10` symbols, `90d` lookback | `5.0s - 8.0s` | `30 req/min` | `Idempotency-Key` required on `POST /jobs` |
| **Agent API** | `/api/v1/agents` | PostgreSQL + Redis Queue | `20` reports/page | `3.0s` (Enqueue/Poll) | `5 req/min` (`POST /runs`) | `Idempotency-Key` required on `POST /runs` |
| **Catalog & Platform API** | `/api/v1/catalog`, `/api/v1/platform` | PostgreSQL | `100` items/page | `3.0s` | `60 req/min` | `PUT` operations naturally idempotent |
| **IAM API** | `/api/v1/auth`, `/api/v1/users` | PostgreSQL | `50` users/page | `2.0s` | `20 req/min` | Standard REST semantics |

---

## 3. Synchronous vs. Asynchronous Execution Contract

To guarantee that expensive operations never tie up FastAPI worker threads or fail due to HTTP gateway timeouts:

1. **Synchronous Boundary ($\le 5\text{ s}$ target execution)**:
   - Any query that can be satisfied via Redis key lookup or bounded ClickHouse partition-pruned scan ($\le 1,000$ rows or pre-aggregated Materialized View) executes synchronously and returns `HTTP 200 OK`.
2. **Asynchronous Job Boundary ($> 5\text{ s}$ or multi-step workflows)**:
   - Historical backfills (`POST /api/v1/historical/backfill-jobs`), heavy multi-month tick analytics (`POST /api/v1/analytics/jobs`), and all AI Agent investigations (`POST /api/v1/agents/runs`) execute asynchronously:
     - **Step 1**: Validate request and `Idempotency-Key` (stored in Redis/PostgreSQL for 24h to prevent duplicate job creation on network retry).
     - **Step 2**: Persist job state (`status = 'QUEUED'`) in PostgreSQL and publish task ID to worker queue.
     - **Step 3**: Return `HTTP 202 Accepted` with `Location: /api/v1/<domain>/<job_id>` and `status: "QUEUED"`.
     - **Step 4**: Client polls `GET /api/v1/<domain>/<job_id>` or subscribes to SSE (`/events`) until `status` reaches `COMPLETED` or `FAILED`.

