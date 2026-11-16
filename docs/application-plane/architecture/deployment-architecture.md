---
doc_id: APP-ARCH-DEP-001
title: "Application Plane Deployment Architecture"
doc_type: architecture
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docker-compose.yml"
    - "deploy/docker/Dockerfile.frontend"
    - "deploy/nginx/nginx.conf"
    - "frontend/vite.config.ts"
related_docs:
  - APP-ARCH-ROOT-001
  - DIAG-APP-DEP-001
  - APP-OPS-RUN-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented Docker Compose serving profiles, Vite dev server vs Nginx production proxy, and container port allocations."
---

# Application Plane Deployment Architecture

## 1. Scope, Context & Runtime Profiles (`docker-compose.yml`)

| Profile / Workload | Container / Process | Ports | State Scope |
|---|---|---|---|
| **Local Dev Frontend** | Vite (`npm run dev`, `frontend/vite.config.ts`) | `3000` | Proxies `/api` and `/ws` -> `127.0.0.1:8000` |
| **Containerized Frontend** | Nginx (`deploy/docker/Dockerfile.frontend`) | `3000` | Serves static ES2022 `dist/` on port `3000` (`listen 3000`) |
| **HTTPS Edge Proxy** | Nginx (`deploy/nginx/nginx.conf`) | `80`, `443` | Redirects HTTP -> HTTPS TLS 1.2/1.3 & proxies to `backend-api:8000` with rate limiting |
| **Default Serving API** | `serving-api` (`src/serving/api/main.py`) | `8000` | Single-process FastAPI + in-memory `PlatformRuntimeContainer` |
| **Microservices Profile** | `svc-api-gateway` (`8000`) + 7 standalone FastAPI containers (`svc-market-hot`, `svc-historical-backfill`, `svc-analytics-quant`, `svc-catalog-governance`, `svc-iam-security`, `svc-intelligence-agent`, `svc-data-plane-v01`) | `8000..8007` | Each container has an isolated empty `PlatformRuntimeContainer` in memory (`GAP`) |

## 2. Building Blocks & Deployment Risks (`AS-IS`)

- **Horizontal Scaling Blocker**: Multiple API workers (`--workers > 1`) or multi-container `--profile microservices` fragment in-memory state (`agent_runs`, `backfill_jobs`, `monitored_instruments`, `detected_anomalies`, `revoked_hashes`).
- **Missing Production TLS Termination**: Compose configures plain HTTP/WS locally; external TLS domain origins in `DomainHttpsEndpointPolicy` (`api.fmdp.io`, etc.) require external reverse proxy / Ingress.
