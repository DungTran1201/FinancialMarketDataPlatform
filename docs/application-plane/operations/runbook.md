---
doc_id: APP-OPS-RUN-001
title: "Application Plane Operational Runbook"
doc_type: specification
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/main.py"
    - "docker-compose.yml"
    - "frontend/package.json"
related_docs:
  - APP-ROOT-001
  - APP-ARCH-DEP-001
  - APP-OPS-INC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented local startup, Compose serving vs frontend builds, health checks, and clean-architecture constraints."
---

# Application Plane Operational Runbook

## 1. Starting API & Frontend Locally (`AS-IS`)

1. **Start Unified FastAPI Gateway (`:8000`)**:
   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn src.serving.api.main:create_unified_gateway_app --factory --host 127.0.0.1 --port 8000
   ```
2. **Start Frontend Vite Dev Server (`:3000`, requires `npm install` + `npm run dev` in `frontend/`)**:
   - Note: Current Windows verification sandbox has no `node`/`npm` installed on PATH (`CAP-APP-FE` build/typecheck externally unverified in this workspace).
3. **Health & Metrics Inspection**:
   - Liveness: `GET http://127.0.0.1:8000/api/v1/health/live`
   - Prometheus exposition: `GET http://127.0.0.1:8000/metrics`

## 2. Operational Warnings (`AS-IS`)

- **Do NOT launch multiple Uvicorn workers (`--workers > 1`)** without shared external state: `agent_runs`, `backfill_jobs`, `monitored_instruments`, and `revoked_hashes` reside strictly in process memory (`APP-ARCH-DATA-001`).
- **Do NOT expose standalone microservice ports (`8001..8007`) directly to untrusted clients** until edge defense middleware (`APP-ARCH-SEC-001`) and Bearer RBAC are added to every wrapper.
