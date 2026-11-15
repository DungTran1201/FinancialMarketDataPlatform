# Platform System Overview

| Metadata | Value |
|---|---|
| **Document ID** | `DOC-OVERVIEW-SYSTEM` |
| **Title** | Financial Market Data Platform System Overview |
| **Category** | Platform Architecture & Orientation |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-15` |
| **Authoring Role** | `documentation-architect` |

---

## 1. Mission & Architectural Vision

The **FinancialMarketDataPlatform (FMDP)** is an enterprise-grade, event-driven quantitative data platform engineered to ingest, stream, process, store, and serve high-throughput financial market data (cryptocurrency & equities) with **zero mock components**, deterministic replayability, and sub-second latency.

The platform unifies **Real-Time Market Streaming**, **Medallion Data Lakehouse**, **Analytical Serving**, and **Agentic AI Intelligence** into a cohesive 3-plane architecture:

```text
                                   ===============================================
                                   EXCHANGE APIS (Binance Spot / Deterministic ASGI)
                                   ===============================================
                                                         │
                                                         ▼
    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ PLANE A: DATA PLANE (Event-Driven Streaming & Medallion Lakehouse)                      │
    │                                                                                        │
    │  Exchange REST / WS ──► Ingestion Engine ──► Kafka Streaming Backbone                  │
    │                                                    ├──► Hot State Consumer ──► Redis   │
    │                                                    ├──► OLAP Consumer ──► ClickHouse   │
    │                                                    └──► Lakehouse Archiver ──► Bronze  │
    │                                                                                  │     │
    │                                   Silver Compacted Parquet (Iceberg v2) ◄────────┘     │
    │                                        │                                               │
    │                                        ▼ (Quality Gate DQ-KLINE-001..005, DQ-TRADE)    │
    │                                   Gold Analytical Marts (Parquet; ClickHouse Target)   │
    └────────────────────────────────────────────────────────────────────────────────────────┘
                                                         │
                                                         ▼
    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ PLANE B: SERVING & APPLICATION GATEWAY PLANE (Modular Monolith & Microservices)        │
    │                                                                                        │
    │  Edge API Gateway (Port 8000) ──► Domain Microservices (svc-* Ports 8001..8007)       │
    │  REST, WebSocket (/ws/v1/observability/stream) & SSE Streams                           │
    │  Experience Layer (Host Port 3001 -> 3000) ──► TypeScript / Vite Single Page App       │
    └────────────────────────────────────────────────────────────────────────────────────────┘
                                                         │
                                                         ▼
    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ PLANE C: AGENTIC INTELLIGENCE PLANE (LangGraph Autonomous Investigation)               │
    │                                                                                        │
    │  LangGraph 5-Node Investigation Engine ──► Controlled Tool Gateway ──► Verified Report │
    └────────────────────────────────────────────────────────────────────────────────────────┘
```

> [!NOTE]
> **Implementation Status (`AS-IS`)**: The v0.1 in-process data platform (`DataPlatformV01Pipeline`), local ZSTD Parquet / Iceberg v2 Lakehouse (`.local_lakehouse`), `55` FastAPI HTTP/WS/SSE routes, `5`-node LangGraph orchestrator (`10` tools), and `8` ASGI microservices (`svc-*`) are **`IMPLEMENTED`**. Standalone daemon CLI loops (`collector-ws`, `collector-rest`, `consumer-lakehouse-bronze`, `agent-worker`; `PROP-APP-002`), distributed Spark/Airflow/GE batch execution, `WS /ws/v1/market/stream`, and route-level domain RBAC (`PROP-APP-004`) remain **`PARTIALLY_IMPLEMENTED` / `PLANNED`**.

---

## 2. The Three Architectural Planes

### 2.1. Plane A: Data Plane (Event Ingestion, Streaming & Lakehouse)
- **Ingestion (`src/ingestion/`)**: Async HTTP REST pagination (`ProductionExchangeHistoricalCollector` with `TokenBucketRateLimiter` `<= 80%` Binance weight) and WebSocket client / gap detection (`SequenceAndGapDetector`). *(Standalone worker CLIs `ws_collector.py` / `rest_backfill.py` are startup stubs; see `PROP-APP-002`.)*
- **Streaming Backbone (`src/streaming/`)**: Partitioned Kafka broker (`PartitionedEventStreamingBroker` / Confluent Kafka adapter) with at-least-once offset ordering and consumer group dispatch.
- **Medallion Lakehouse (`src/lakehouse/`)**:
  - **Bronze**: Immutable ZSTD-compressed Parquet files written locally to `.local_lakehouse` (`bronze/{event_type}/provider={p}/ingestion_date={date}`; MinIO `lakehouse-*` buckets provisioned as S3 target).
  - **Silver**: Deduplicated, compacted time-series Parquet tables with Apache Iceberg v2 snapshot metadata manifests.
  - **Gold**: Curated analytical marts (`fct_daily_market_summary`, `fct_realized_volatility`, `fct_orderbook_liquidity`) guarded by blocking financial data quality rules (`DQ-KLINE-001..005`, `DQ-TRADE-001..003`).

### 2.2. Plane B: Serving & Application Plane
- **API Gateway & Modular Monolith (`src/serving/api/`)**: Unified FastAPI gateway (`55` HTTP/WS/SSE routes), JWT `HS256` IAM module, sliding-window rate limiting, and Nginx TLS edge proxy (`deploy/nginx/nginx.conf`).
- **Dual Deployment Modes (`ADR-007`)**:
  - `IN_PROCESS_ASGI`: Single-process Modular Monolith dispatching via `httpx.ASGITransport` for low-overhead local dev and CI.
  - `REMOTE_HTTP_CONTAINER`: Standalone container processes across domain microservices (`docker compose --profile core --profile microservices up -d`).
- **Frontend Experience (`frontend/`)**: TypeScript/Vite SPA providing real-time data flow visualization, candlestick charts, latency histograms, and system health views.

### 2.3. Plane C: Agentic Intelligence Plane
- **Investigation Orchestrator (`src/intelligence/orchestrator/`)**: **5-node** LangGraph state graph (`intake_and_guardrail_node` -> `investigation_planner_node` -> `tool_gateway_executor_node` -> `evidence_verifier_node` -> `report_synthesizer_node`).
- **Controlled Tool Gateway (`src/intelligence/tools/`)**: Sandboxed invocation across `10` deterministic read-only tools ensuring provenance tracking.

---

## 3. Core Architectural Decision Records (ADRs)

| ADR ID | Title | Key Architectural Principle |
|---|---|---|
| [ADR-001](../architecture/adr/ADR-001-overall-architecture.md) | Modular Monolith & 3-Plane Separation | Strict boundaries preventing coupling across planes |
| [ADR-002](../architecture/adr/ADR-002-event-driven-data-platform.md) | Event-Driven Streaming Platform | Kafka event streaming with at-least-once delivery |
| [ADR-003](../architecture/adr/ADR-003-storage-strategy.md) | Polyglot Storage Strategy | Parquet/Iceberg for cold lakehouse, Redis for hot state, ClickHouse for OLAP |
| [ADR-004](../architecture/adr/ADR-004-backend-architecture.md) | Clean Architecture Backend Modules | Domain entities independent of infrastructure adapters |
| [ADR-005](../architecture/adr/ADR-005-query-and-caching-strategy.md) | Hot Caching & Query Strategy | Two-tier caching with sub-millisecond hot lookups |
| [ADR-006](../architecture/adr/ADR-006-agent-integration.md) | Agentic Intelligence Integration | LangGraph autonomous investigation with tool guardrails |
| [ADR-007](../architecture/adr/ADR-007-microservices-and-data-platform-v01.md) | Zero-Mock E2E Data Platform v0.1 | 12-stage production data lifecycle & microservice profiles |
| [ADR-008](../architecture/adr/ADR-008-event-driven-modular-data-platform.md) | Modular Restructuring & Domain Alignment | Source tree organized by functional architecture |

