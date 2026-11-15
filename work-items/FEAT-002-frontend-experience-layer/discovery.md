# Work Item Discovery — FEAT-002

| Metadata | Value |
|---|---|
| **Work Item ID** | `FEAT-002` |
| **Change Type** | `FEAT` |
| **Risk Tier** | `R2` |
| **Status** | `DISCOVERY_COMPLETED` |
| **Created Date** | `2026-11-15` |
| **Updated Date** | `2026-11-15` |

---

## 1. Discovery Evidence Register

### FACT 1: Backend Headless API Status
- `src/serving/api/main.py` provides 8 domain contexts plus unified telemetry routes under `/api/v1/observability/*` and WebSocket stream under `/ws/v1/observability/stream`.
- Static assets in `src/serving/api/gateway/ui.py` were decommissioned in `FEAT-001` to keep the backend serving plane headless and clean.

### FACT 2: Node.js & Tooling Environment
- Node.js `v24.18.0` and npm `11.16.0` are active in the workspace environment.
- Vite `v6.x` and TypeScript `v5.7.x` provide zero-bloat compilation, high-speed HMR, and bundling to standard HTML/CSS/JS.

### FACT 3: Protocol & Port Topology
- Nginx edge gateway (`deploy/nginx/nginx.conf`) terminates TLS 1.3 on port 443 and redirects port 80.
- Application backend operates internally on `backend-api:8000`.
- Frontend SPA container runs on port 3000, exposed locally on port 3001.

### DECISION 1: Pure TypeScript Single Page Application (SPA)
- Rather than introducing heavy opinionated frontend frameworks, the Experience Layer uses clean modular TypeScript with a lightweight reactive store, client-side hash routing, and native HTML5 Canvas/SVG charts.

### DECISION 2: Controlled Data Access
- All browser interactions go exclusively through FastAPI endpoints (`/api/v1/*`, `/ws/v1/*`). No direct TCP connections to databases or brokers.

