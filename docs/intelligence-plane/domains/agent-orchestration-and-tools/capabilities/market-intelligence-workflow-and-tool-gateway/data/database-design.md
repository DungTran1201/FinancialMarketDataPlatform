---
doc_id: CAP-INT-ORC-DB-001
title: "Physical Database Design & Migration Plan: Agent State Persistence"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: NOT_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: database-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "deploy/postgres/init/01_schema.sql"
    - "src/serving/infrastructure/runtime.py"
    - ".env.example"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-DM-001
  - DIAG-INT-ORC-ERD-001
  - APP-ARCH-DATA-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Documented PostgreSQL 16 agent_runs and agent_tool_invocations DDL, runtime unwired status, least-privilege roles, and required schema migrations."
---

# Physical Database Design & Migration Plan: Agent State Persistence

## 1. Physical Storage Engines (`AS-IS` Memory vs `TARGET` PostgreSQL 16)

- **`AS-IS` Runtime**: Zero SQL driver code (`asyncpg`, `sqlalchemy`, `psycopg`) executes inside `src/intelligence/` or `src/serving/`. `agent_runs`, `idempotency_keys`, `reports`, and `ControlledToolGateway._audit_log` exist strictly in RAM.
- **`TARGET` Physical Store**: PostgreSQL 16 (`fmdp_control` database initialized by `deploy/postgres/init/01_schema.sql:41-66`) accessed by `agent-worker` and `svc-intelligence-agent` using least-privilege account `POSTGRES_AGENT_USER=fmdp_agent_rw` (`.env.example:73`). Note: `.env.example` declares `fmdp_agent_rw`, `fmdp_app_rw`, and `fmdp_agent_ro` (ClickHouse), **but** `01_schema.sql` currently creates only tables under `fmdp_pg_admin` and does **not** provision `GRANT` statements for `fmdp_agent_rw`!

## 2. Declared Tables & Indexes (`deploy/postgres/init/01_schema.sql`)

| Table | Engine / Constraints | Indexes | `AS-IS` Implementation |
|---|---|---|---|
| `agent_runs` | `run_id UUID PK`, `trigger_mode CHECK ('ON_DEMAND', 'EVENT_TRIGGERED')`, `requested_by UUID FK -> users(id)`, `symbol VARCHAR(32)`, `status CHECK ('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')`, `prompt_summary TEXT`, `structured_report JSONB`, `token_usage JSONB`, `started_at TIMESTAMPTZ`, `completed_at TIMESTAMPTZ` | `idx_agent_runs_status_started ON agent_runs (status, started_at DESC)` | `NOT_IMPLEMENTED` in runtime (DDL exists only) |
| `agent_tool_invocations` | `invocation_id UUID PK`, `run_id UUID FK -> agent_runs(run_id) ON DELETE CASCADE`, `tool_name VARCHAR(64)`, `input_params JSONB`, `output_metadata JSONB`, `status CHECK ('SUCCESS', 'TIMEOUT', 'VALIDATION_ERROR', 'SOURCE_ERROR')`, `started_at TIMESTAMPTZ` | `idx_agent_tools_run_id ON agent_tool_invocations (run_id, started_at ASC)` | `NOT_IMPLEMENTED` in runtime (DDL exists only) |

## 3. Required Schema Evolution Before Production Cutover (`OPEN-INT-004`)

1. Add `idempotency_key VARCHAR(128)` with a unique partial index (`WHERE idempotency_key IS NOT NULL`) on `agent_runs`.
2. Add workflow checkpoint columns (`visited_nodes JSONB`, `current_iteration INT`, `max_iterations INT`, `token_budget INT`, `worker_lease_expires_at TIMESTAMPTZ`, `error_detail TEXT`) or configure LangGraph PostgreSQL checkpointer tables.
3. Harmonize `agent_tool_invocations.status` CHECK constraint to include `PERMISSION_DENIED`.
4. Provision explicit PostgreSQL `ROLE` & `GRANT SELECT, INSERT, UPDATE` permissions for `fmdp_agent_rw` (excluding `users` password hashes) and ClickHouse `SELECT` grants for `fmdp_agent_ro`.
5. Standardize `run_id` generation to canonical UUIDv4 (`str(uuid.uuid4())`) instead of `run_<hex12>` (or change PK type via migration).

