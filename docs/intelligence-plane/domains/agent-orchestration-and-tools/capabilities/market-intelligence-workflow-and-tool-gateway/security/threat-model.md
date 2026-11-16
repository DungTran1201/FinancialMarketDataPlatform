---
doc_id: CAP-INT-ORC-TM-001
title: "Threat Model: Market Intelligence Workflow & Tool Gateway"
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
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/reporting/validator.py"
    - "src/serving/infrastructure/runtime.py"
    - "src/serving/api/modules/agent_api/presentation/router.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - INT-ARCH-SEC-001
  - CAP-INT-ORC-SEC-001
  - CAP-INT-ORC-POL-001
  - DIAG-INT-ORC-TM-001
requirement_ids:
  - THR-INT-001
  - THR-INT-002
  - THR-INT-003
  - THR-INT-004
  - THR-INT-005
  - THR-INT-006
  - THR-INT-007
  - THR-INT-008
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Completed capability threat model covering assets, entry points, trust boundaries, AS-IS vs TARGET LLM threat scenarios, mitigations, and residual risks."
---

# Threat Model: Market Intelligence Workflow & Tool Gateway

Derived visual diagram: [threat-model-diagram.md](threat-model-diagram.md) (`DIAG-INT-ORC-TM-001`).

## 1. Protected Assets, Entry Points & Trust Boundaries

- **Assets**: Market data integrity (`HotStateProjector`, `ClickHouseBatchSink`), anomaly detection cooldown state (`StatisticalAnomalyDetector._cooldown_registry`), `runtime.detected_anomalies`, `runtime.reports` (`StructuredAnalysisReport`), `AgentWorkflowState` history, external LLM API credentials (`LLM_API_KEY` `TARGET`), and compute/token budgets.
- **Entry Points**:
  1. `PlatformRuntimeContainer.execute_agent_investigation()` invoked by unauthenticated `POST /api/v1/agents/runs` (`:8000` and `:8006`).
  2. `MarketIntelligenceGraph.run_investigation()` (`symbol`, `prompt_summary`, `trigger_mode`).
  3. `ControlledToolGateway.execute_tool()` (`tool_name`, `params`, `granted_permissions`).
  4. `ReportValidator.validate_report()` (`report`, `evidence_trail`).
  5. `TARGET` External LLM response JSON and Kafka `market.anomalies.v1` consumer.
- **Trust Boundaries**:
  - `TB-INT-1`: Application Plane API ingress -> Intelligence Graph intake.
  - `TB-INT-2`: Model Adapter / Planner -> `ControlledToolGateway`.
  - `TB-INT-3`: `ControlledToolGateway` -> Data Plane & State Mutation Handlers.
  - `TB-INT-4`: Intelligence Orchestrator -> External LLM Provider (`TARGET`).

## 2. Threat Scenarios, Mitigations & Residual Risk

| Threat ID | Threat Scenario & Scope (`AS-IS` vs `TARGET`) | Severity | `AS-IS` Mitigations & Verified Gaps | Required Mitigation (`TARGET`) | Residual Risk |
|---|---|---|---|---|---|
| `THR-INT-001` | **Unauthorized Agent Trigger & Hardcoded Role Escalation (`AS-IS` ACTIVE)**: Any unauthenticated HTTP client (or `VIEWER`) calls `POST /api/v1/agents/runs`; `MarketIntelligenceGraph` hardcodes `self._agent_permissions` granting `agent:trigger` + all read scopes (`graph.py:117`). | `CRITICAL` | `:8000` applies IP rate limit (`5 req/min`), `:8006` has none; zero `Depends` auth guard (`SEC-AUDIT-003`). | Enforce JWT/API-key `agent:trigger` at API ingress AND pass caller capability intersection into `run_investigation()`. | `CRITICAL` (`BLOCKED`) |
| `THR-INT-002` | **Cooldown Exhaustion / Anomaly State Pollution via `detect_anomalies` (`AS-IS` ACTIVE)**: Calling `detect_anomalies` mutates `anomaly_detector._cooldown_registry` (900s suppression) and appends to `runtime.detected_anomalies` (`runtime.py:493-495`). | `HIGH` | Protected only by mock planner's fixed 1-call-per-run plan today; callable directly or repeatedly by an external LLM in `TARGET`. | Split read-only dry-run anomaly evaluation (`evaluate_only=True`) from alert emission, or require explicit write/approval gate. | `HIGH` (`OPEN`) |
| `THR-INT-003` | **Report Overwrite / Unmarked Write Tool (`AS-IS` ACTIVE)**: `generate_analysis_report` mutates `runtime.reports[run_id]` while `ToolGovernancePolicy.is_read_only_market_data` defaults to `True` (`contracts.py:35,102`). | `MEDIUM` | Only Node 5 invokes Tool #10 under mock adapter, using unique `run_id`. | Mark `is_read_only_market_data=False`, prevent LLM direct call to `generate_analysis_report`, and disallow overwriting `COMPLETED` reports. | `MEDIUM` (`OPEN`) |
| `THR-INT-004` | **Numeric Fabrication Behind Valid Citations (`AS-IS` PARTIAL / `TARGET` HIGH)**: `ReportValidator` checks `invocation_id` set membership only (`validator.py:29-30`); an external LLM can fabricate prices/returns in `summary` text while citing real IDs. | `HIGH` | Mock adapter copies tool output deterministically (`AS-IS`). | Add deterministic numeric-fact cross-checking and citation metadata equality checks before enabling external LLM. | `HIGH` (`OPEN`) |
| `THR-INT-005` | **Resource / Token / Thread Exhaustion (`AS-IS` ACTIVE)**: `POST /agents/runs` awaits full workflow synchronously; `AGENT_RUN_TIMEOUT_SECONDS=90` is unimplemented; Node 5 runs outside budget check; `PlatformConfig` caps are ignored. | `HIGH` | `max_iterations=6`, planning token cap `6400`, per-tool `asyncio.wait_for` (`1.5s–8s`). | Decouple into async `agent-worker` queue, enforce outer run timeout, bind `PlatformConfig` caps, and cover Node 5 in budget. | `HIGH` (`OPEN`) |
| `THR-INT-006` | **Prompt Injection & Tool Parameter Tampering (`TARGET` HIGH / `AS-IS` DORMANT)**: `prompt_summary` or poisoned market strings manipulate external LLM into calling unexpected tools or passing negative/malformed `params` (`limit=-1`). | `HIGH` | `AS-IS` mock ignores `prompt_summary`; whitelist & upper `limit` enforced. `AS-IS` lacks Pydantic schema validation (`limit <= 0`, type errors). | Strict Pydantic input schemas per tool, prompt role isolation, and fail-closed on missing handlers (`remove stub_ok`). | `MEDIUM` (`TARGET`) |
| `THR-INT-007` | **Silent Fallback Masking Missing Market Data (`AS-IS` ACTIVE)**: Handlers (`runtime.py:453,466,480,492`) substitute static `[89500.0, ...]` arrays on missing ClickHouse data while report sets `"data_quality_status": "HEALTHY"`. | `MEDIUM` | Mock disclaimer notes `adapter=mock`, not fallback arrays. | Raise explicit missing-data status or set `data_quality_status="DEGRADED"` when fallback/stale data is used. | `MEDIUM` (`OPEN`) |
| `THR-INT-008` | **LLM Provider Compromise & Secret/Prompt Leakage (`TARGET`)**: `LLM_API_KEY` leak or proprietary `prompt_summary` retention at external LLM vendor. | `MEDIUM` | No external LLM SDKs or outbound calls exist `AS-IS`. | Secret vault injection, redaction filters in logs, and approved vendor DPA/ZDR policy (`OPEN-INT-001`). | `OPEN` (`TARGET`) |

