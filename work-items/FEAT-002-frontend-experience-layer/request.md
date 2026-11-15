# Work Item Request — FEAT-002

| Metadata | Value |
|---|---|
| **Work Item ID** | `FEAT-002` |
| **Title** | `Independent Frontend Experience Layer (TypeScript, HTML5, CSS3)` |
| **Change Type** | `FEAT` |
| **Risk Tier** | `R2` |
| **Status** | `ACTIVE` |
| **Requested By** | `Senior Frontend Architect / User` |
| **Created Date** | `2026-11-15` |
| **Updated Date** | `2026-11-15` |

---

## 1. Change Summary & Intent

Engineer and integrate an independent **Experience / Presentation Layer** into the `FinancialMarketDataPlatform` system architecture, communicating with the Application Plane (Plane B) via REST API, WebSocket, and SSE.

## 2. In-Scope Objectives

- Build an independent TypeScript SPA under `frontend/` powered by Vite, HTML5, and CSS3.
- Establish the 6 core UI modules:
  1. **Overview Dashboard**: High-level KPIs, market summary, and core stores health grid.
  2. **Data Flow**: 12-stage interactive SVG DAG, parallel-branch latency decomposition, Kafka partition lag table, and 10-timestamp event trace drawer.
  3. **Market Analytics**: Real-time Canvas Candlestick Chart (1m to 1d), top-20 order book depth, annualized realized volatility, Pearson correlation matrix, and statistical anomalies.
  4. **Data Management**: Medallion Dataset Registry (Bronze/Silver/Gold), schema field inspector, end-to-end data lineage, and Great Expectations quality gates.
  5. **AI Workspace**: LangGraph 5-node workflow state machine, on-demand investigation triggers, provenance citations inspector, and verified markdown report viewer.
  6. **Administration**: User persona (RBAC), API key generation and revocation, rate limit tiers, and defense-in-depth parameters.
- Provide typed API client, resilient auto-reconnecting WebSocket client, SSE stream client, and observable stores.
- Containerize via multi-stage `deploy/docker/Dockerfile.frontend`, integrate into `docker-compose.yml`, and configure `deploy/nginx/nginx.conf`.
- Synchronize canonical models (`models/ux/ux.yaml`, `models/architecture/components.yaml`) and C4 diagrams (`docs/diagrams/system/02-c4-container.md`).

## 3. Out-of-Scope Boundaries

- Direct browser connections to internal databases (Kafka, Redis, ClickHouse, PostgreSQL, MinIO).
- Altering existing Backend business logic or Clean Architecture boundaries.
- Adding heavyweight external UI frameworks.

## 4. Constraints & Non-Negotiables

- Strict client-server decoupling.
- Zero mock data presented as live data.
- Pass `tools/validators/run_all.py` and `npm test` with 0 errors.

