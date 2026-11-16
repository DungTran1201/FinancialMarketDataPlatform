---
doc_id: CAP-INT-ORC-POL-001
title: "Side-Effect Governance, Tool Permission Matrix & Human Approval Policy"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/orchestrator/graph.py"
    - "src/serving/infrastructure/runtime.py"
    - "src/serving/api/modules/iam/domain/ports.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-TM-001
  - CAP-INT-ORC-SEC-001
  - DIAG-INT-ORC-AUTHZ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Documented tool permission matrix, AS-IS hardcoded workflow permissions, side-effect discrepancies, and human approval policy."
---

# Side-Effect Governance, Tool Permission Matrix & Human Approval Policy

Authoritative machine-readable rules: [authorization-matrix.yaml](authorization-matrix.yaml). Derived flow diagram: [agent-tool-authorization-flow.md](agent-tool-authorization-flow.md) (`DIAG-INT-ORC-AUTHZ-001`).

## 1. Tool Permission Matrix & Hardcoded Workflow Warning (`AS-IS` vs `TARGET`)

> [!CAUTION]
> **`AS-IS` Hardcoded Permission Disclosure**: `MarketIntelligenceGraph.__init__()` (`src/intelligence/orchestrator/graph.py:117`) hardcodes `self._agent_permissions = frozenset({"market:read", "historical:read", "analytics:read", "agent:trigger"})` and passes it to every `execute_tool()` call. Consequently, **user-based RBAC authorization is NOT enforced at workflow runtime** (`CAP-APP-AGT-001` HTTP routes also omit JWT checks).

| Permission Scope (`ROLE_CAPABILITIES`) | Roles Holding Scope (`iam/domain/ports.py`) | Tools Requiring Scope (`APPROVED_TOOL_POLICIES`) | `AS-IS` Runtime Enforcement |
|---|---|---|---|
| `market:read` | `viewer`, `analyst`, `operator`, `admin` (`service` missing!) | `get_latest_price`, `get_market_snapshot`, `get_data_freshness` | Checked inside `ControlledToolGateway` against hardcoded `_agent_permissions`. |
| `historical:read` | `viewer`, `analyst`, `operator`, `admin` | `get_historical_candles` | Checked inside `ControlledToolGateway` against hardcoded `_agent_permissions`. |
| `analytics:read` | `viewer`, `analyst`, `operator`, `admin` | `get_market_statistics`, `calculate_returns`, `calculate_volatility`, `calculate_correlation`, `detect_anomalies` | Checked inside `ControlledToolGateway` against hardcoded `_agent_permissions`. |
| `agent:trigger` | `analyst`, `operator`, `admin` (denied to `viewer` in IAM domain) | `generate_analysis_report` (and `TARGET` API trigger `POST /api/v1/agents/runs`) | Checked in unit tests (`test_contracts_and_guardrails.py:160-165`), **bypassed at runtime** by hardcoded `_agent_permissions` and unauthenticated API. |

## 2. Side-Effect Classification & Human Approval Policy

| Tool | `AS-IS` Side Effect | `ToolGovernancePolicy` Flag (`contracts.py:35`) | Blast Radius & `TARGET` Control Policy | Human Approval Gate |
|---|---|---|---|---|
| `generate_analysis_report` | Overwrites `runtime.reports[run_id]` (`TARGET`: updates Postgres `agent_runs.structured_report`). | **BUG**: `is_read_only_market_data=True` (default). | Set `is_read_only_market_data=False`; block LLM planner from invoking directly (orchestrator Node 5 only after `ReportValidator`); prohibit overwriting `COMPLETED` runs. | **NOT REQUIRED** (automated deterministic provenance check `ReportValidator` gates report creation; external trading/execution actions remain out of platform scope). |
| `detect_anomalies` | Mutates `StatisticalAnomalyDetector._cooldown_registry` (900s suppression) and appends to `runtime.detected_anomalies`. | **BUG**: `is_read_only_market_data=True` (default). | Refactor into pure read-only statistical evaluation (`side-effect-free`) when called by Agent tools, reserving cooldown mutation exclusively for Data Plane `StatisticalAnomalyDetector` pipeline events (`OPEN-INT-002`). | **NOT APPLICABLE** once refactored to read-only; while state-mutating `AS-IS`, risk is mitigated only by mock planner's single invocation per run. |
| Tools 1–7, 9 (`get_*`, `calculate_*`) | Read-only memory queries + `_audit_log` append. | `is_read_only_market_data=True` | Enforce strict read-only DB accounts (`fmdp_agent_ro`) and input schema validation (`SEC-INT-002`). | **NONE** (read-only). |
| **Future External / Trading / Destructive Tools** | Out of current scope (`NOT_IMPLEMENTED`). | N/A | Any future tool modifying market catalog, external webhooks, or financial orders MUST require explicit human-in-the-loop approval before execution (`GOV-STD-AGENT-001`). | **MANDATORY HUMAN APPROVAL** (`BLOCKING` policy rule). |

