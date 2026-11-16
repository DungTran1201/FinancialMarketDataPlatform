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
    - "src/serving/infrastructure/runtime.py"
    - "docker-compose.yml"
related_docs:
  - INT-ROOT-001
  - INT-OPS-INC-001
  - INT-OPS-SLO-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Authored Intelligence Plane runbook covering startup/shutdown, runtime/worker health, audit inspection, and resource budgets."
---

# Intelligence Plane Operational Runbook

## 1. Startup & Shutdown (`AS-IS` vs `TARGET`)

- **Active `AS-IS` Execution**: Investigations run inside `fmdp-backend-api` (`src/serving/api/main.py` via `PlatformRuntimeContainer`). Starting and stopping `backend-api` starts/stops Plane C execution.
- **Standalone Worker (`src/intelligence/main.py`, `--profile intelligence`)**:
  ```powershell
  python -m src.intelligence.main
  ```
  - **Important**: `main()` logs `max_iterations`, `tool_timeout`, and `max_tokens` and **exits immediately** (`AS-IS` stub). It does not stay alive or poll a queue.

## 2. Runtime, Worker & Provider Health

- **Runtime Health**: Verify Plane B `/api/v1/health/live` and `/api/v1/agents/runs` responsiveness.
- **Worker Health (`TARGET`)**: Once `agent-worker` polls PostgreSQL `agent_runs`, add a heartbeat/liveness probe to `--profile intelligence`.
- **Model Provider Availability**: `AS-IS` uses offline `DeterministicMockLLMAdapter` (`LLM_PROVIDER=mock`). `TARGET` external LLM providers require checking outbound HTTPS/API key validity and fallback status.

## 3. Audit Inspection & Resource Budgets

- **Audit Inspection (`AS-IS`)**: `ControlledToolGateway._audit_log` and `PlatformRuntimeContainer.agent_runs` / `reports` live in process memory only (accessible via `GET /api/v1/agents/runs/{run_id}` and `GET /api/v1/reports/{run_id}`).
- **Audit Inspection (`TARGET`)**: Query PostgreSQL `agent_runs` and `agent_tool_invocations` (`deploy/postgres/init/01_schema.sql`).
- **Resource Budgets**: `AgentWorkflowState` defaults to `max_iterations=6` and `token_budget=8000` (80% planning cap = `6400`); `PlatformConfig` reads `AGENT_MAX_ITERATIONS`, `AGENT_TOOL_TIMEOUT_SECONDS`, `AGENT_MAX_TOKENS_PER_RUN`, though `runtime.py` currently uses `AgentWorkflowState` defaults.

