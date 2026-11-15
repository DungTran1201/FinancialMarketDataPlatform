# 09 — API and Integration Architecture

## 1. API Design Principles & Protocol Selection

The Backend Application Plane exposes three distinct client communication protocols, each matched to its interaction semantics:

| Protocol | Base Path | Status & Use Case | Why Selected |
|---|---|---|---|
| **REST over HTTP/HTTPS (JSON)** | `/api/v1/*` | **`IMPLEMENTED`**: Synchronous resource queries (latest prices, historical klines/trades, market stats, catalog, IAM, observability, v0.1 data-plane) and asynchronous job submission (`202 Accepted` on `/agents/runs` and `/historical/backfill-jobs`). | Cacheable, stateless, OpenAPI 3.1 contract, universal client support. |
| **WebSocket (WS/WSS)** | `/ws/v1/observability/stream` (`IMPLEMENTED`); `/ws/v1/market/stream` (`PLANNED`) | Live observability snapshot streaming (`IMPLEMENTED` in `observability.py`); live market ticker/kline multiplex feed (`PLANNED`). | Eliminates HTTP polling overhead over persistent connections. |
| **Server-Sent Events (SSE)** | `/api/v1/agents/runs/{run_id}/events`, `/api/v1/observability/stream` | **`IMPLEMENTED`**: Unidirectional progress notifications for LangGraph runs and live platform observability snapshots. | Standard HTTP stream compatible with bearer headers and native browser `EventSource` reconnection. |

### Strict Client Isolation Rule
- Browsers, desktop apps, and external API consumers **never** connect directly to Apache Kafka, Redis, ClickHouse, PostgreSQL, or MinIO. All external traffic terminates at `backend-api` (or `edge-gateway` / `superset` for authenticated internal BI users).

---

## 2. API Domain Boundaries, Runtime Rate Limits & Query Guardrails

See also: [API Specification](../specifications/api-specification.md), [Canonical API Model](../../models/api/api.yaml), and [Diagram 09: Backend Request Lifecycle](../diagrams/backend/09-backend-request-lifecycle.md).

> [!NOTE]
> **Runtime Rate Limit & RBAC Enforcement Disclosure**:
> - `SlidingWindowRateLimiter` (`src/serving/api/main.py` middleware) enforces 4 path buckets: `/api/v1/auth*` (`10 req/min`), `/api/v1/agents/runs*` (`5 req/min`), `/api/v1/analytics*` (`30 req/min`), and default (`120 req/min`) across all other routes.
> - Route-level JWT/RBAC dependencies currently execute on `/api/v1/auth/*` (`API-039..043`) and `ControlledToolGateway`; non-IAM domain routers do not yet attach FastAPI `Depends(...)` auth guards (`runtime_rbac_enforced: false`, tracked in `PROP-APP-004`).

| API Domain | Prefix | Primary Storage / Runtime Target | Guardrails / Runtime Notes | Runtime Rate Limit (`SlidingWindowRateLimiter`) | Idempotency / Method Notes |
|---|---|---|---|---|---|
| **Market API** | `/api/v1/market` | Redis Hot Projection + ClickHouse Fallback (in-memory/adapter in v0.1) | `/prices`, `/prices/{symbol}`, `/snapshots/{symbol}`, `/orderbook/{symbol}` (`API-001..002`, `API-023..024`) | `120 req/min` | Read-only `GET` |
| **Historical Data API** | `/api/v1/historical` | ClickHouse (`Reads`), SQLite/PG Watermarks (`Jobs`) | `/klines/{symbol}`, `/trades/{symbol}`, `POST/GET /backfill-jobs` (`API-004..006`, `API-035`) | `120 req/min` | `Idempotency-Key` target (`PARTIALLY_IMPLEMENTED` on `POST /backfill-jobs`) |
| **Analytics API** | `/api/v1/analytics` | ClickHouse MV + Quant adapters | `/statistics/{symbol}`, `/correlations`, `/anomalies`, `POST /anomalies/evaluate` (`API-007`, `API-036..038`) | `30 req/min` | Statistical analysis & evaluation |
| **Agent & Reporting API** | `/api/v1/agents`, `/api/v1/reports` | LangGraph Orchestrator + PG/SQLite run store | `POST /runs`, `GET /runs/{id}`, `SSE /runs/{id}/events`, `GET /reports`, `GET /reports/{id}` (`API-008..009`, `API-043..045`) | `5 req/min` on `/agents/runs*`; `120 req/min` on `/reports` | `Idempotency-Key` optional/target on `POST /runs` |
| **Catalog & Platform API** | `/api/v1/catalog`, `/api/v1/platform` | Instrument / Freshness / Config stores | `/instruments`, `PUT /instruments/{symbol}`, `/freshness`, `/lakehouse/pipeline`, `/platform/config` (`API-025`, `API-039..042`) | `120 req/min` | `PUT` operations naturally idempotent |
| **IAM API** | `/api/v1/auth` | In-memory / PostgreSQL IAM (`PBKDF2-HMAC-SHA256`, `HS256` JWT) | `POST /token`, `POST /verify`, `POST /revoke`, `POST /api-keys`, `GET /domains` (`API-026..030`); note `/api/v1/users` does not exist | `10 req/min` | JWT + API-Key SHA-256 management |
| **Data Platform v0.1 & Microservices API** | `/api/v1/data-platform/v01`, `/api/v1/microservices` | `DataPlatformV01Pipeline` (`12 stages`), `MicroserviceRegistry` | `/run`, `/gold/{mart}`, `/compaction`, `/lineage`, `/metrics`, `/topology` (`API-011..015`, `API-050..054`) | `120 req/min` | Pipeline execution & governance inspection |
| **Observability & Health API** | `/api/v1/observability`, `/api/v1/health`, `/metrics` | `DataObservabilityMetricsCollector`, Hub | `/snapshot`, `/stages`, `SSE/WS /observability/stream`, `/health/{live,ready}` (`API-016..022`, `API-055..056`) | `120 req/min` | Read / telemetry streaming |

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

