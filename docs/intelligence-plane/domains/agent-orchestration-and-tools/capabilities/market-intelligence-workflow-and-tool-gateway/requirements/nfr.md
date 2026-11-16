---
doc_id: CAP-INT-ORC-NFR-001
title: "Non-Functional Requirements: Market Intelligence Workflow & Tool Gateway"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: devops-sre
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/shared/config/settings.py"
    - ".env.example"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-REQ-001
  - INT-OPS-SLO-001
requirement_ids:
  - NFR-INT-001
  - NFR-INT-002
  - NFR-INT-003
  - NFR-INT-004
  - NFR-INT-005
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Defined Intelligence Plane NFRs with explicit TARGET_UNRESOLVED markers where latency/availability benchmarks are unapproved."
---

# Non-Functional Requirements: Market Intelligence Workflow & Tool Gateway

> [!NOTE]
> Per Documentation V2 governance (`GOV-STD-NFR-001`), unconfirmed latency, throughput, availability, RTO, and RPO targets are recorded as `TARGET_UNRESOLVED [OPEN]` rather than invented.

## 1. Measurable Quality Requirements

| NFR ID | Quality Attribute | Requirement Statement | Approved Target (or `TARGET_UNRESOLVED`) | Workload / Environment Condition | Verification Method |
|---|---|---|---|---|---|
| `NFR-INT-001` | **Per-Tool Execution Timeout** | Each tool invocation MUST be bounded by its `ToolGovernancePolicy.timeout_seconds` (`1.5s`–`8.0s`) via `asyncio.wait_for`. | `1.5s` (`get_latest_price`), `2.0s` (`get_market_snapshot`), `3.0s` (`get_data_freshness`, `generate_analysis_report`), `5.0s` (candles/stats/returns/vol/anomalies), `8.0s` (`calculate_correlation`) — enforced in `gateway.py:79` | Asyncio runtime; `PlatformConfig.agent_tool_timeout_seconds=5.0` currently unwired | Unit/Contract Timeout Test (`NOT_RUN` for timeout exception path) |
| `NFR-INT-002` | **End-to-End Investigation Run Latency & Timeout** | Whole investigation run duration MUST be bounded so slow LLM providers or tools cannot hang workers or API handlers. | `TARGET_UNRESOLVED [OPEN]` (`.env.example` suggests `AGENT_RUN_TIMEOUT_SECONDS=90`, unloaded in `settings.py` and unenforced in `graph.py`) | Single `ON_DEMAND` or `EVENT_TRIGGERED` run (`mock` vs external LLM) | Benchmark after async worker & external LLM wiring |
| `NFR-INT-003` | **Bounded Resource & Token Budget** | Each run MUST cap iterations (`max_iterations=6`) and planning tokens (`80%` of `token_budget=8000` -> `6400`), preventing runaway LLM loops. | `max_iterations=6`, `token_budget=8000` (code defaults; `PlatformConfig` wiring `OPEN`) | Per investigation run | Unit / Integration Inspection (`graph.py:131`, `investigation.py:37-43`) |
| `NFR-INT-004` | **Determinism & Numerical Precision** | Monetary prices and volumes read from Data Plane MUST preserve `Decimal` string fidelity; analytical math MUST execute deterministically in Python. | Zero LLM prompt arithmetic (`ADR-OVR-003`) | All 10 tools (`quant.py` uses IEEE `float` internally for `math.log`/`math.sqrt` transcendental steps) | Unit & Integration Tests (`test_contracts_and_guardrails.py`) |
| `NFR-INT-005` | **Availability, Durability & Recovery** | Queued/running agent workflows and generated reports MUST survive process restarts and isolate failures from Plane B serving HTTP threads. | `TARGET_UNRESOLVED [OPEN]` (`RPO/RTO` unapproved; `AS-IS` is ephemeral in-memory inside FastAPI process) | Multi-container Compose (`--profile intelligence`) | Architecture Inspection & Recovery Drill (`BLOCKED` until Postgres wired) |

## 2. Graceful Degradation & Failure Boundaries

| Dependency Outage / Fault | Required System Behavior (`TARGET`) | `AS-IS` Observed Reality | Blast Radius Containment |
|---|---|---|---|
| **External LLM Outage / Timeout (`TARGET`)** | Retry boundedly on `429`/`5xx`, then degrade to deterministic summary (tagged in `limitations_disclaimer`) or mark run `FAILED`. | Offline `DeterministicMockLLMAdapter` never makes network calls (`SIMULATED`). | `ON_DEMAND` API returns `202` immediately (`TARGET`); `AS-IS` inline call would block FastAPI worker. |
| **ClickHouse / Redis Unavailability** | Tool handlers return explicit `SOURCE_ERROR` / degraded flag (`data_quality_status != "HEALTHY"`). | `calculate_*` and `detect_anomalies` silently fall back to hardcoded static price arrays while report still sets `"data_quality_status": "HEALTHY"` (`GAP`). | Data Plane ingestion & streaming remain unaffected. |
| **PostgreSQL Checkpoint Failure (`TARGET`)** | Worker marks lease retryable or fails run cleanly without corrupting completed reports. | Zero Postgres persistence wired (`agent_runs` / `reports` live in memory dicts only). | Process restart loses all run history and reports. |

