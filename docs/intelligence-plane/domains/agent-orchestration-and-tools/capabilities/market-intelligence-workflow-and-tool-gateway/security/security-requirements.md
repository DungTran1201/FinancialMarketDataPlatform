---
doc_id: CAP-INT-ORC-SEC-001
title: "Security Requirements: Market Intelligence Workflow & Tool Gateway"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/reporting/validator.py"
    - "deploy/postgres/init/01_schema.sql"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-TM-001
  - CAP-INT-ORC-POL-001
  - CAP-APP-IAM-SEC-001
requirement_ids:
  - SEC-INT-001
  - SEC-INT-002
  - SEC-INT-003
  - SEC-INT-004
  - SEC-INT-005
  - SEC-INT-006
  - SEC-INT-007
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Mapped OWASP ASVS / NIST SSDF informed security controls (SEC-INT-001..007) to threats, AS-IS verification, and remediation blockers."
---

# Security Requirements: Market Intelligence Workflow & Tool Gateway

## 1. Security Control Requirements (`SEC-INT-*`)

| Security ID | Mitigated Threat(s) | Control Requirement | `AS-IS` Verification Reality | Target Verification / Remediation |
|---|---|---|---|---|
| `SEC-INT-001` | `THR-INT-001` | Caller RBAC capabilities (`agent:trigger` + read scopes) MUST be authenticated at Plane B and propagated to `MarketIntelligenceGraph`; hardcoded `_agent_permissions` MUST be removed (`ASVS V4`). | **FAILING GAP**: `MarketIntelligenceGraph` hardcodes `_agent_permissions`; `POST /agents/runs` unauthenticated (`SEC-AUDIT-003`). | Pass `JwtClaims.capabilities` from authenticated caller; reject `VIEWER` role (`test_security_and_defense.py`). |
| `SEC-INT-002` | `THR-INT-006` | `ControlledToolGateway` MUST allow only `ApprovedAgentTool` members, validate strict Pydantic input schemas (`limit >= 1`, valid `symbol`, `BoundedTimeRange`), and fail closed if a handler is unregistered. | **PARTIAL**: Whitelist & upper `limit` verified (`test_contracts_and_guardrails.py`); lower bounds, schema validation, and missing-handler fail-closed (`stub_ok`) are unimplemented. | Add per-tool Pydantic validators and raise explicit error when handler is `None`. |
| `SEC-INT-003` | `THR-INT-002`, `THR-INT-003` | State-mutating tools (`generate_analysis_report`, `detect_anomalies`) MUST declare `is_read_only_market_data=False`, enforce write/idempotency rules, and restrict planner-initiated side effects. | **FAILING GAP**: `ToolGovernancePolicy.is_read_only_market_data` defaults to `True` on all 10 tools; `detect_anomalies` mutates global cooldown state. | Separate read-only anomaly evaluation from alert publication; prevent planner from directly invoking persistence tools. |
| `SEC-INT-004` | `THR-INT-004` | Reports MUST cite valid `invocation_id`s from `evidence_trail`, match provenance metadata (`tool_name`, `symbol`, `row_count`), and pass numeric consistency checks before persistence (`ASVS V5`). | **PARTIAL**: `ReportValidator` checks non-empty `provenance_citations` and `invocation_id` membership (`test_three_planes_framework.py`); numeric/field parity checks missing. | Extend `ReportValidator` with metadata parity & quantitative value verification before external LLM use. |
| `SEC-INT-005` | `THR-INT-005` | Agent runs MUST enforce bounded iterations, total token budget (including Node 5), per-tool timeout, and whole-run `AGENT_RUN_TIMEOUT_SECONDS`, executing outside HTTP threads. | **PARTIAL**: Planning loop caps & per-tool `asyncio.wait_for` implemented; outer run timeout, `PlatformConfig` cap wiring, and async worker missing. | Wire `PlatformConfig` limits, wrap `run_investigation()` in `asyncio.wait_for`, and execute in `agent-worker`. |
| `SEC-INT-006` | `THR-INT-001`..`005` | All tool invocations (including `PERMISSION_DENIED`, `VALIDATION_ERROR`, `TIMEOUT`) MUST emit structured audit records without exposing secrets, SQL strings, or stack traces. | **PARTIAL**: `ControlledToolGateway._audit_log` records `SUCCESS` envelopes in memory only; failed attempts raise unhandled without audit entries. | Persist all invocation outcomes to PostgreSQL `agent_tool_invocations` under `fmdp_agent_rw`. |
| `SEC-INT-007` | `THR-INT-008` | `LLM_API_KEY` and DB credentials MUST reside strictly in environment/secret store, redacted from logs/reports, and Data Plane DB connections MUST use least-privilege accounts (`fmdp_agent_ro`, `fmdp_agent_rw`). | **PARTIAL (`AS-IS` mock)**: No `LLM_API_KEY` used `AS-IS`; `.env.example` defines roles, but `01_schema.sql` lacks `GRANT` statements and runtime has no DB drivers. | Add explicit Postgres/ClickHouse least-privilege `GRANT` scripts and secret redaction tests. |

## 2. Secret & Audit Hygiene Rules

- Real API keys (`LLM_API_KEY`), JWT signing keys, and database passwords MUST NEVER appear in `AgentWorkflowState`, `StructuredAnalysisReport`, `limitations_disclaimer`, or test fixtures.
- `ControlledToolGateway` audit logs MUST sanitize error details before persisting or returning to `CAP-APP-AGT-001`.

