---
doc_id: INT-OPS-RUN-001
title: "Intelligence Plane Operational Runbook"
doc_type: specification
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: devops-sre
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/main.py"
    - "src/serving/api/main.py"
    - "src/serving/api/services/intelligence.py"
    - "docker-compose.yml"
    - ".env.example"
related_docs:
  - INT-ROOT-001
  - INT-OPS-INC-001
  - INT-OPS-SLO-001
  - APP-OPS-RUN-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented startup, health probes, worker stub behavior, audit inspection, and resource budget procedures for Plane C."
---

# Intelligence Plane Operational Runbook

## 1. Startup, Shutdown & Runtime Hosting (`AS-IS` vs `TARGET`)

### 1.1 Active `AS-IS` Hosting (Inside FastAPI Process)

Because `src/intelligence/main.py` exits immediately after logging initialization, operational Intelligence Plane execution currently occurs **in-process** inside:
- Unified Gateway (`backend-api`, port `8000`): `uvicorn src.serving.api.main:app --host 0.0.0.0 --port 8000`
- Optional microservice wrapper (`svc-intelligence-agent`, port `8006`): `uvicorn src.serving.api.services.intelligence:create_intelligence_microservice_app --factory --host 0.0.0.0 --port 8006`
- **Operational Constraint**: Do **NOT** launch multiple Uvicorn worker processes (`--workers > 1`) and do **NOT** route traffic across `:8000` and `:8006` simultaneously expecting shared state — `agent_runs`, `reports`, `idempotency_keys`, and `ControlledToolGateway._audit_log` are process-local Python dicts/lists.
- **Shutdown**: FastAPI lifespan calls `PlatformRuntimeContainer.close()` (`main.py:85`), closing SQLite watermark handles; all in-memory Plane C runs and reports are discarded upon shutdown.

### 1.2 Standalone `agent-worker` Entrypoint (`docker-compose.yml --profile intelligence`)

- Running `python -m src.intelligence.main` logs `Initialized agent-worker (max_iterations=..., tool_timeout=..., max_tokens=...)` and exits with code `0` (`NOT_IMPLEMENTED` queue loop). Compose does not define a healthcheck on `agent-worker` (`docker-compose.yml:327-348`).

## 2. Health, Provider Availability & Audit Inspection Procedures

1. **API Health Probes (`AS-IS`)**:
   - Unified host liveness/readiness: `GET /api/v1/health/live` and `GET /api/v1/health/ready` (`main.py:119-125`).
   - Standalone microservice liveness: `GET /api/v1/health/live` on port `8006` (`services/intelligence.py:24-31`).
2. **Model Provider Mode Check**:
   - Inspect `.env` (`LLM_PROVIDER`, `LLM_MODEL_NAME`); note that `AS-IS` code always constructs `DeterministicMockLLMAdapter()` (`runtime.py:174`) regardless of `.env` until external LLM wiring is implemented.
3. **Run & Audit Trail Inspection (`AS-IS`)**:
   - List recent runs: `GET /api/v1/agents/runs?limit=20`.
   - Inspect visited nodes, `tokens_consumed`, `evidence_trail` (`invocation_id`, `source_store`, `row_count`), and `final_report`: `GET /api/v1/agents/runs/{run_id}`.
   - Inspect persisted reports: `GET /api/v1/reports` and `GET /api/v1/reports/{run_id}`.
   - (`TARGET` PostgreSQL inspection once wired): Query `agent_runs` and `agent_tool_invocations` ordered by `started_at`.
4. **Resource Budget Verification**:
   - Default workflow caps are `max_iterations=6` and `token_budget=8000` (`6400` planning ceiling). Note that `AGENT_MAX_ITERATIONS` and `AGENT_MAX_TOKENS_PER_RUN` in `PlatformConfig` are **not** yet wired into `execute_agent_investigation()` (`runtime.py:579`).

