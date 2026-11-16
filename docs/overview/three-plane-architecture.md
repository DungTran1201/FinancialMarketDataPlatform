---
doc_id: OVR-ARCH-3P-001
title: "Three-Plane Architecture & Ownership Boundaries"
doc_type: architecture
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/main.py"
    - "src/serving/infrastructure/runtime.py"
    - "tests/architecture/test_clean_architecture_boundaries.py"
related_docs:
  - OVR-ROOT-001
  - OVR-ARCH-XPL-001
  - OVR-DIAG-3P-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Documented Three-Plane ownership model vs actual runtime composition roots on 7880c85."
---

# Three-Plane Architecture & Ownership Boundaries

Derived visual view: [three-plane-architecture.md](diagrams/three-plane-architecture.md) (`DIAG-OVR-3P-001`).

## 1. Scope & Architectural Premise `[REQUIRED]`

FMDP separates documentation, domain ownership, contracts, and AST module boundaries into **three Planes** (`data-plane`, `application-plane`, `intelligence-plane`) plus a shared kernel (`src/shared/`). Importantly, the three-plane model defines **logical ownership and dependency boundaries**: in the `AS-IS` runtime, all three Planes execute within the single FastAPI `PlatformRuntimeContainer` process (`src/serving/infrastructure/runtime.py`) alongside optional standalone Compose service declarations.

## 2. Context & External Boundaries `[REQUIRED]`

Each Plane owns strictly bounded code modules, contracts, persistence schemas, and runtime processes (when deployed independently):

- **Shared Kernel (`src/shared/`)**: Immutable value objects, quant math, `EventEnvelopeV1`, `CanonicalDatasetContract`, cryptography/WAF/rate-limit primitives, Prometheus collector, tracing registry, and `PlatformConfig`. Cannot import from any Plane (`test_clean_architecture_boundaries.py:89-136`).

## 3. Building Block, Ownership & Dependency Structure `[REQUIRED]`

| Plane | Owned Packages & UI Roots | Owned Responsibilities | Owned Contracts & Data | Allowed Upstream Deps | Prohibited Dependencies |
|---|---|---|---|---|---|
| **Data Plane** | `src/ingestion/`, `src/streaming/`, `src/lakehouse/` | External market acquisition, normalization, Kafka topics & DLQ routing, hot cache & OLAP batch projection, anomaly detection, Bronze/Silver/Gold storage, DQ gates, lineage | `EventEnvelopeV1`, 6 Kafka topics (`market.raw.*`, `market.anomalies.v1`, `market.dlq.v1`), Redis hash keys, ClickHouse tables, SQLite/Postgres watermarks, `.local_lakehouse/` Parquet | `src/shared/`, external Binance feeds (ingestion) | MUST NOT import `src/serving/` or `src/intelligence/` (`test_clean_architecture_boundaries.py`) |
| **Application Plane** | `src/serving/`, `frontend/` | HTTP/REST API gateway, SSE/WS observability stream, browser SPA screens, IAM JWT/API-key/middleware defense, catalog/platform config, `PlatformRuntimeContainer` composition root, `DataPlatformV01Pipeline` trigger API | Capability `openapi.yaml` contracts, UI screen routes, Postgres `users` & `monitored_instruments` (Target) | `src/shared/`, reads/invokes Data Plane ports/handlers (`runtime.py`) and queues Intelligence runs | Domain layers MUST NOT import FastAPI/drivers; Plane MUST NOT embed LLM prompts or compute raw ML inference |
| **Intelligence Plane** | `src/intelligence/` | Agent workflow orchestrator (`MarketIntelligenceGraph`), deterministic LLM adapters, `ControlledToolGateway` whitelist/RBAC/bounds, citation validation (`ReportValidator`) | Tool contracts (`ApprovedAgentTool`), `AgentWorkflowState`, `ToolExecutionEnvelope`, `StructuredAnalysisReport`, Postgres `agent_runs` / `agent_tool_invocations` (Target) | `src/shared/`, accesses market/analytics data strictly via injected gateway handlers (`runtime.py`) | MUST NOT bypass `ControlledToolGateway`, issue raw SQL, execute orders, or write directly to hot/analytical market tables |

## 4. Current Implementation (`AS-IS`) vs. Target Process Isolation `[REQUIRED]`

| Concern | `AS-IS` Runtime Reality (`7880c85`) | `TARGET` Architecture Intent | Gap / Risk |
|---|---|---|---|
| **Process Boundary** | `src/serving/api/main.py` runs `PlatformRuntimeContainer` holding Data Plane engines, Plane B APIs, and Plane C `MarketIntelligenceGraph` in one Python process. Standalone Docker workers (`collector-*`, `consumer-*`, `agent-worker`) exit immediately. | Separate worker processes (`collector-ws`, `collector-rest`, `consumer-hot-redis`, `consumer-analytics-ch`, `consumer-lakehouse-bronze`, `agent-worker`) communicating over Kafka, Redis, ClickHouse, Postgres, MinIO. | Microservice wrappers (`services/*.py`) cannot share in-memory dicts across containers (`GAP-ARCH-001`). |
| **Failure Propagation** | Shared process means an unhandled CPU/memory spike or unhandled exception in inline pipeline execution (`POST /data-platform/v01/run` or synchronous `202` routes) shares the API gateway process. | Async queue/topic decoupling (`Kafka` topics + `agent_runs` queue in Postgres) isolates ingestion spikes & slow LLM calls from interactive market read APIs. | Async background worker queues (`202` decoupling) are `NOT_IMPLEMENTED`. |
| **Security Trust Zones** | `PlatformRuntimeContainer` calls Python methods directly in-process without TLS or mTLS/token verification between planes; `SEC-AUDIT-001..003` leave HTTP unauthenticated. | Defense-in-depth Edge Nginx + verified JWT/RBAC on every endpoint + least-privilege DB roles (`fmdp_api_reader`, `fmdp_agent_ro`, `fmdp_ingest_writer`, `fmdp_agent_rw`). | `BLOCKED` until IAM & DB backing are implemented. |
