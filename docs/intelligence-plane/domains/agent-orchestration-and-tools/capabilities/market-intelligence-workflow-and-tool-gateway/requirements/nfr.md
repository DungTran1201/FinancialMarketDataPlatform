---
doc_id: CAP-INT-ORC-NFR-001
title: "Non-Functional Requirements: Market Intelligence Workflow & Tool Gateway"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/shared/config/settings.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-REQ-001
  - INT-OPS-SLO-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented NFRs for tool timeouts, loop bounds, clean architecture isolation, and OPEN latency/availability targets."
---

# Non-Functional Requirements (`CAP-INT-ORC-001`)

| NFR ID | Category | Requirement | `AS-IS` Status & Evidence |
|---|---|---|---|
| `NFR-INT-001` | **Bounded Execution** | Planning loop MUST cap iterations at `max_iterations=6` and tokens at `80%` of `token_budget=8000` (`6400`). | `IMPLEMENTED` (`investigation.py:37-43`); Node 5 runs outside cap. |
| `NFR-INT-002` | **Tool Timeout Enforcement** | Each tool invocation MUST enforce its policy `timeout_seconds` (`1.5s`–`8.0s`). | `IMPLEMENTED` via `asyncio.wait_for()` (`gateway.py:79`). |
| `NFR-INT-003` | **Run Timeout** | End-to-end investigation run MUST enforce `AGENT_RUN_TIMEOUT_SECONDS` (`90s` in `.env.example`). | `NOT_IMPLEMENTED` (env var not loaded in `settings.py`). |
| `NFR-INT-004` | **Query Row Bounds** | Tool queries MUST NOT exceed `max_rows_or_periods` (`1` to `2160`). | `IMPLEMENTED` for upper bound (`gateway.py:64-69`); lower bound `<=0` unchecked. |
| `NFR-INT-005` | **Subsystem Isolation** | `src/intelligence/` MUST NOT import `ingestion`, `streaming`, `lakehouse`, or `serving`. | `VERIFIED` by `test_clean_architecture_boundaries.py`. |
| `NFR-INT-006` | **Latency & Availability** | Target P95 investigation latency and worker availability SLOs. | `OPEN` (`OPEN-INT-001`: requires benchmark after external LLM & Postgres wiring). |

