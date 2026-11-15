# Financial Market Data Platform — Experience / Presentation Layer (`frontend/`)

## 1. Overview & Architectural Role

The **Frontend Experience Layer** is an independent, modular, high-performance Single Page Application (SPA) designed to provide operational monitoring, deep market analytics, pipeline observability, and agentic interaction for the **Real-time Financial Market Data Platform**.

It connects to the **FastAPI Application & Control Plane (Plane B)** via:
1. **REST API (`/api/v1/*`)**: Structured transactional, analytical, governance, and control queries.
2. **Server-Sent Events (`/api/v1/observability/stream`)**: Real-time push updates for topology nodes, KPI pulses, and 10-timestamp event lifecycle traces.
3. **WebSocket (`/ws/v1/observability/stream`)**: Bidirectional streaming for telemetry and market depth.

---

## 2. Directory Structure

```text
frontend/
├── public/
│   ├── assets/                # Static brand graphics and favicons
│   └── icons/                 # Public SVG icons
├── src/
│   ├── app/
│   │   ├── router/            # Client-side hash router with route lifecycle hooks
│   │   ├── layouts/           # Main shell (Header, Sidebar, Status Bar, Viewport)
│   │   └── providers/         # Global context and lifecycle initializers
│   ├── modules/
│   │   ├── dashboard/         # Module 1: Overview Dashboard (KPIs, stores health)
│   │   ├── data-flow/         # Module 2: 12-Stage Data Flow & SVG DAG visualizer
│   │   ├── market-analytics/  # Module 3: Candlestick chart & Quant analytics
│   │   ├── data-management/   # Module 4: Medallion Catalog, Schemas, Lineage & DQ
│   │   ├── ai-workspace/      # Module 5: LangGraph 5-node workflow & reports
│   │   └── administration/    # Module 6: IAM, RBAC, API Keys & Security params
│   ├── components/
│   │   ├── ui/                # Reusable UI primitives (Buttons, Cards, Badges, Drawers)
│   │   ├── charts/            # High-performance Canvas Candlestick & Volume chart
│   │   ├── diagrams/          # Zoomable interactive SVG Pipeline DAG
│   │   └── tables/            # Reusable DataTables with sort/filter
│   ├── services/
│   │   ├── api/               # Typed fetch clients (Market, Observability, Catalog, etc.)
│   │   ├── websocket/         # Resilient auto-reconnecting WebSocket client
│   │   └── auth/              # JWT Token, session storage, and API key management
│   ├── hooks/                 # Custom reactive utility hooks
│   ├── stores/                # Observable/Pub-Sub State Stores (App, Market, Observability)
│   ├── types/                 # Complete TypeScript schema contracts
│   ├── utils/                 # Formatting (currency, latency, timestamps, DOM helpers)
│   └── styles/                # CSS3 Design tokens, variables, layout, components, animations
├── tests/                     # Unit and integration test suites
├── package.json               # Node.js dependencies and npm scripts
├── tsconfig.json              # Strict TypeScript compiler options
├── vite.config.ts             # Vite bundler configuration & local reverse proxy
└── README.md                  # This documentation
```

---

## 3. The Six Core UI Modules

| Module | Route | Architectural Purpose & Data Sources |
|---|---|---|
| **1. Overview Dashboard** | `#/dashboard` | High-level KPIs (Total Ingested, E2E Latency P50/P99, Active Kafka Lag, DLQ counts) and Core Stores Health Grid (Kafka, Redis, ClickHouse, Postgres, MinIO). |
| **2. Data Flow** | `#/data-flow` | Interactive zoomable SVG DAG illustrating the 12-stage data platform, parallel-branch latency decomposition (Redis Hot vs. ClickHouse OLAP vs. MinIO Lakehouse), Kafka partition/broker lag inspector, and 10-timestamp event trace drawer. |
| **3. Market Analytics** | `#/market-analytics` | Real-time Canvas Candlestick Chart (OHLCV 1m to 1d), Top-20 Order Book Depth (sub-15ms Redis), Annualized Realized Volatility, Pearson Correlation Matrix, and Statistical Market Anomalies. |
| **4. Data Management** | `#/data-management` | Medallion Dataset Registry (Bronze/Silver/Gold), Schema Inspector (field types, nullability, natural keys), End-to-End Data Lineage graph, and Great Expectations Quality Gates report. |
| **5. AI Workspace** | `#/ai-workspace` | LangGraph 5-Node Workflow State Machine (`intake_and_classify` $\rightarrow$ `publish_report`), on-demand investigation triggers, Provenance Citations inspector (zero-hallucination verification), and Markdown report viewer. |
| **6. Administration** | `#/administration` | Current user persona (Admin/Analyst/Operator/Viewer), API Key lifecycle (generation and SHA-256 revocation), Sliding Window rate-limit quotas, and defense-in-depth parameters. |

---

## 4. Architectural Invariants & Boundary Rules

1. **Strict Client-Server Isolation**: The frontend runs completely client-side in the user's browser. It has **zero direct connection** to Apache Kafka, Redis, ClickHouse, PostgreSQL, or MinIO. All communication flows through the API Gateway (FastAPI Plane B).
2. **Separation of Concerns**:
   - `services/api/`: Handles network transport, Bearer token injection, and error normalization.
   - `stores/`: Manages reactive business and presentation state without framework dependencies.
   - `components/`: Pure rendering and event emission.
   - `modules/`: Feature-scoped business composition.
3. **Truth & Reality Honesty**:
   - Explicit distinction between `LIVE` mode (real exchange/ClickHouse data) and `DEMO` mode (synthetic test events).
   - Kafka cluster reporting accurately reflects the single-node KRaft local deployment (Broker 1 active; Broker 2 and 3 reported as `UNAVAILABLE`).
4. **Content Security Policy (CSP) Compliance**:
   - Zero external CDN scripts or stylesheet dependencies.
   - All styling, fonts, and scripts are served locally.

---

## 5. Development & Build Commands

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start local development server with hot module replacement (HMR)
# Proxies /api and /ws to http://localhost:8000
npm run dev

# Run unit and integration tests
npm test

# Build optimized production bundle to dist/
npm run build

# Preview production build locally on port 3000
npm run preview
```

---

## 6. Docker & Production Deployment

The frontend is containerized using a multi-stage Docker build (`deploy/docker/Dockerfile.frontend`).

In `docker-compose.yml`:
```yaml
frontend:
  build:
    context: .
    dockerfile: deploy/docker/Dockerfile.frontend
  container_name: fmdp-frontend
  profiles: ["core", "frontend"]
  ports:
    - "127.0.0.1:3000:3000"
  depends_on:
    backend-api:
      condition: service_healthy
  networks:
    - frontend_net
```

