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
                                   =============================================
                                   EXCHANGE APIS (Binance, CoinGecko, Deterministic)
                                   =============================================
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
    │                                        ▼ (Quality Gate DQ-KLINE-001..005)              │
    │                                   Gold Analytical Marts (DuckDB / ClickHouse)          │
    └────────────────────────────────────────────────────────────────────────────────────────┘
                                                         │
                                                         ▼
    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ PLANE B: SERVING & APPLICATION GATEWAY PLANE (Modular Monolith & Microservices)        │
    │                                                                                        │
    │  Edge API Gateway (Port 8000) ──► Market Hot (8001) / Historical (8002) / Quant (8003) │
    │  WebSockets & Server-Sent Events (SSE) ──► Real-Time Stream Clients                    │
    │  Experience Layer (Port 3000) ──► Modern TypeScript/Vite Single Page Application       │
    └────────────────────────────────────────────────────────────────────────────────────────┘
                                                         │
                                                         ▼
    ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ PLANE C: AGENTIC INTELLIGENCE PLANE (LangGraph Autonomous Investigation)               │
    │                                                                                        │
    │  LangGraph 6-Node Investigation Engine ──► Controlled Tool Gateway ──► Verified Report │
    └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Three Architectural Planes

### 2.1. Plane A: Data Plane (Event Ingestion, Streaming & Lakehouse)
- **Ingestion (`src/ingestion/`)**: Production-grade async HTTP REST pagination (`httpx.AsyncClient`) with token-bucket rate limiting (`<= 80%` Binance limit) and real-time WebSocket connection handling with sequence gap detection.
- **Streaming Backbone (`src/streaming/`)**: Partitioned Kafka broker with at-least-once offset ordering and consumer group dispatch.
- **Medallion Lakehouse (`src/lakehouse/`)**:
  - **Bronze**: Immutable ZSTD-compressed Parquet files partitioned by `provider/ingestion_date`.
  - **Silver**: Deduplicated, compacted time-series data maintained as Apache Iceberg v2 snapshot manifests.
  - **Gold**: Curated analytical marts (`fct_daily_market_summary`, `fct_realized_volatility`, `fct_orderbook_liquidity`) guarded by blocking financial data quality rules (`DQ-KLINE-001..005`).

### 2.2. Plane B: Serving & Application Plane
- **API Gateway (`src/serving/api/`)**: Unified edge router providing JWT authentication, HMAC token verification, rate limiting, and reverse proxy routing.
- **Dual Deployment Modes (`ADR-007`)**:
  - `IN_PROCESS_ASGI`: Single-process Modular Monolith dispatching via `httpx.ASGITransport` for low-overhead local dev and CI.
  - `REMOTE_HTTP_CONTAINER`: Standalone container processes across 8 domain microservices (`docker compose --profile microservices up`).
- **Frontend Experience (`frontend/`)**: Modern TypeScript/Vite SPA providing real-time data flow visualization, candlestick charts, latency histograms, and system health metrics.

### 2.3. Plane C: Agentic Intelligence Plane
- **Investigation Orchestrator (`src/intelligence/orchestrator/`)**: 6-node LangGraph state graph for autonomous anomaly investigation, market trend analysis, and root-cause determination.
- **Controlled Tool Gateway (`src/intelligence/tools/`)**: Sandboxed tool invocation ensuring provenance logging and strict data boundaries.

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
