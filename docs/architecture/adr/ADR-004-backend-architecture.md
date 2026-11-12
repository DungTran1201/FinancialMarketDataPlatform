# ADR-004: Modular Monolith Backend with Clean/Hexagonal Architecture & Selective CQRS

- **Status**: Accepted
- **Date**: 2026-11-12
- **Deciders**: Backend Architecture Team

---

## 1. Decision Title

Structure the Backend as a **FastAPI Modular Monolith** internally organized by business domains using **Clean / Hexagonal Architecture (Ports & Adapters)** and **Selective CQRS**, paired with **Independently Deployable Workers** for ingestion, streaming consumption, batch processing, and Agent execution.

---

## 2. Context

The platform requires a unified API surface covering Market Data, Historical Data, Analytics, Data Catalog, User/Authentication, Platform Configuration, Agent Intelligence, and Reporting. At the same time, it requires background processes that maintain persistent WebSocket connections to Binance, consume Kafka partitions continuously, execute heavy batch pipelines, and run multi-step LangGraph workflows.

---

## 3. Problem Statement

How do we design the backend architecture so that:
1. It avoids premature microservices sprawl and network overhead in local/constrained environments,
2. Domain business rules remain decoupled from FastAPI, Redis, ClickHouse, PostgreSQL, and Kafka SDKs,
3. Read-heavy market/analytical workloads are separated from write-side ingestion without over-engineering simple CRUD modules, and
4. Long-running or CPU-intensive tasks never block the FastAPI async event loop?

---

## 4. Selected Option

### 4.1. Deployment Topology: Modular Monolith + Independent Workers
1. **FastAPI Modular Monolith (`backend-api`)**:
   - Single deployable API service containing domain modules: `market`, `historical`, `analytics`, `catalog`, `iam` (User & Auth), `platform_config`, `agent_api`, and `reporting`.
2. **Independently Deployable Workers**:
   - `collector-ws` & `collector-rest`: Stateful/scheduled ingestion workers.
   - `consumer-hot-redis`, `consumer-analytics-ch`, `consumer-lakehouse-bronze`: Kafka streaming consumers.
   - `agent-worker`: Dedicated Intelligence Plane worker executing LangGraph workflows and anomaly investigations.

### 4.2. Internal Module Pattern: Clean / Hexagonal Architecture
Every domain module enforces strict inward dependency rules (`Presentation -> Application -> Domain <- Infrastructure`):
- **Domain Layer**: Pure Python entities, value objects, domain exceptions, and repository/service port protocols (`typing.Protocol` / `ABC`). Zero framework or I/O imports.
- **Application Layer**: Command handlers, query handlers, use cases, and DTOs orchestrating domain ports.
- **Infrastructure Layer**: Concrete adapters for Redis, ClickHouse, PostgreSQL, Kafka, and external HTTP clients.
- **Presentation Layer**: FastAPI routers, Pydantic HTTP request/response schemas, auth dependencies, and rate-limit middleware.

### 4.3. Selective CQRS (Without Event Sourcing)
- **Applied to Market, Historical, and Analytics domains**:
  - **Write Path**: Collectors $\rightarrow$ Kafka $\rightarrow$ Streaming Consumers / Batch Pipelines $\rightarrow$ Redis, ClickHouse, Iceberg.
  - **Read Path**: FastAPI Query Handlers read directly from read-optimized projections (Redis for Hot queries, ClickHouse tables & Materialized Views for Historical/Analytical queries).
- **NOT applied to IAM, Platform Configuration, or Catalog CRUD**:
  - Standard transactional Command/Query repositories over PostgreSQL without separate read-model synchronization overhead.

---

## 5. Alternative Options Considered

### Alternative A: Microservice per Domain (`market-service`, `historical-service`, `analytics-service`, `auth-service`, `catalog-service`)
- **Rejection Reason**: Violates Section 6.1 and 9.1. Deploying 8 separate FastAPI containers requires an API gateway, inter-service RPC/auth propagation, duplicated connection pools to PostgreSQL/ClickHouse/Redis, and $8\times$ base Python process memory overhead with zero architectural benefit at initial scale.

### Alternative B: Layered CRUD / ActiveRecord Architecture (Routers Directly Querying SQLAlchemy / ClickHouse Clients)
- **Rejection Reason**: Couples HTTP transport schemas directly to storage engines, makes unit testing impossible without live databases, and prevents clean fallback logic (such as transparent Redis-to-ClickHouse fallback).

### Alternative C: Full CQRS + Event Sourcing Across All Domains (Including Users and Configuration)
- **Rejection Reason**: Violates Section 6.3 and 9.3. Reconstructing user accounts or platform settings from an event log adds massive complexity without business value.

---

## 6. Decision Rationale

- **Modular Monolith** provides a single unified OpenAPI specification, shared in-process authentication/RBAC validation, and shared database connection pools, while keeping domain packages strictly decoupled so any module (such as `agent_api` or `market`) can be extracted into a standalone service later by swapping an in-process adapter for an HTTP/gRPC adapter.
- **Clean/Hexagonal Architecture** guarantees that domain rules and financial calculations can be tested deterministically in milliseconds using in-memory fakes.
- **Worker Separation** guarantees that WebSocket ingestion, Kafka consumption, and LLM orchestration never compete with HTTP request handling on the FastAPI event loop.

---

## 7. Benefits

- **Fast Local Development & Debugging**: One API codebase to run, test, and inspect; clear package boundaries enforced by automated import-linter/architecture tests.
- **Event Loop Protection**: FastAPI only performs non-blocking async I/O (reading Redis, querying ClickHouse/PostgreSQL, or enqueuing jobs); all heavy work happens in worker processes.
- **Clean Extraction Path**: Because modules communicate via Application Services / Ports rather than cross-importing internal infrastructure repositories, future service extraction requires no domain rewrite.

---

## 8. Drawbacks

- Requires discipline (and automated architecture tests) to prevent developers from bypassing ports or importing across domain internals.
- Selective CQRS means read models in Redis and ClickHouse are eventually consistent with ingestion streams.

---

## 9. Architectural Limitations

- FastAPI's `async def` coroutines run on a single-threaded event loop per worker process; any synchronous CPU-bound calculation (e.g., large Pandas/NumPy matrix math) executed directly inside a route handler will block all concurrent requests on that worker. All analytical math must either be pushed down to ClickHouse SQL or offloaded to background workers.
- In-process background tasks (`fastapi.BackgroundTasks`) are ephemeral and lost if the API container restarts; durable asynchronous workflows (Backfills, Agent Runs, Heavy Analytics) must persist state in PostgreSQL and execute in dedicated workers.

---

## 10. Operational Implications

- Run FastAPI via Uvicorn with configurable worker processes (`WEB_CONCURRENCY=2` locally) behind health check endpoints (`/api/v1/health/live`, `/api/v1/health/ready`).
- Enforce architectural dependency rules in CI (`tests/architecture/test_clean_architecture_boundaries.py`).

---

## 11. Consequences

- All domain modules under `src/backend/modules/<domain>/` follow a standardized four-subpackage structure: `domain/`, `application/`, `infrastructure/`, and `presentation/`.
- Cross-module communication goes exclusively through public `application/` interfaces or shared `src/shared/` contracts.

---

## 12. Conditions That Could Invalidate This Decision

1. If WebSocket broadcast fan-out (`WS /ws/v1/market/stream`) grows to tens of thousands of concurrent client connections, the WebSocket gateway module should be extracted from the REST API monolith into a dedicated horizontally scaled WebSocket edge service backed by Redis Pub/Sub.

