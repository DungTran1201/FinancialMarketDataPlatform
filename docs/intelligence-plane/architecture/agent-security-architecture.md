---
doc_id: INT-ARCH-SEC-001
title: "Intelligence Plane Security Architecture & Threat Surface"
doc_type: architecture
plane: intelligence-plane
scope_level: plane
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
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - INT-ARCH-GW-001
  - CAP-INT-ORC-TM-001
  - CAP-INT-ORC-SEC-001
  - DIAG-INT-GW-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Mapped Intelligence Plane trust boundaries and separated active AS-IS vulnerabilities from future external-LLM risks."
---

# Intelligence Plane Security Architecture & Threat Surface

Derived diagrams: [tool-gateway-boundaries.md](diagrams/tool-gateway-boundaries.md) (`DIAG-INT-GW-001`) and [threat-model-diagram.md](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/threat-model-diagram.md) (`DIAG-INT-ORC-TM-001`).

## 1. Scope and Trust Boundaries

The Intelligence Plane mediates autonomous execution between untrusted user/market inputs and internal data/state stores.

### 1.1 Trust Boundaries

1. **TB-INT-1 (Application Trigger -> Workflow Intake)**: Caller `POST /api/v1/agents/runs` crosses from Application Plane (`CAP-APP-AGT-001`) into `PlatformRuntimeContainer.execute_agent_investigation()`.
2. **TB-INT-2 (Workflow / LLM Planner -> `ControlledToolGateway`)**: Untrusted or LLM-selected `tool_name` and `params` cross into `ControlledToolGateway.execute_tool()`.
3. **TB-INT-3 (`ControlledToolGateway` -> Data Plane / State Stores)**: Handler closures read `HotStateProjector` / `ClickHouseBatchSink` and write `runtime.reports` / `runtime.detected_anomalies` (`TARGET`: least-privilege DB roles `fmdp_agent_ro` and `fmdp_agent_rw`).
4. **TB-INT-4 (Orchestrator -> External LLM Provider) `[TARGET]`**: `prompt_summary` and market evidence cross network egress to third-party LLM APIs (`OPEN`).

## 2. Context: Active `AS-IS` Risks vs Future External-LLM (`TARGET`) Risks

Security analysis MUST distinguish vulnerabilities exploitable right now (`AS-IS` with `DeterministicMockLLMAdapter`) from risks introduced only when an external LLM provider is enabled (`TARGET`).

| Risk Category | `AS-IS` Status (Current Code Reality) | `TARGET` Risk (When External LLM Enabled) |
|---|---|---|
| **Unauthorized Agent Invocation** | **ACTIVE CRITICAL GAP (`SEC-AUDIT-003`)**: `POST /api/v1/agents/runs` has zero FastAPI `Depends` JWT/RBAC guards (`agent_api/router.py:45`). `svc-intelligence-agent` (`:8006`) also lacks edge middleware (`services/intelligence.py`). | Remains critical until Bearer JWT + `agent:trigger` RBAC guard is enforced at every ingress. |
| **Privilege Escalation & Hardcoded Permissions** | **ACTIVE HIGH GAP**: `MarketIntelligenceGraph` hardcodes `self._agent_permissions = frozenset({"market:read", "historical:read", "analytics:read", "agent:trigger"})` (`graph.py:117`). A `VIEWER` caller (or unauthenticated caller) gains `agent:trigger` privileges inside Plane C. | Must derive `granted_permissions` strictly from authenticated caller `JwtClaims.capabilities` intersected with service ceiling. |
| **Tool Abuse & Parameter Tampering** | Whitelist & positive `limit` upper bound enforced (`gateway.py:51-69`), **but** negative/zero limits (`-1`), missing Pydantic type checks, and missing `start_time`/`end_time` span bounds (`BoundedTimeRange`) are unvalidated. | External LLM tool calls could inject malformed types, negative limits, or invalid `report` payloads into `generate_analysis_report`. |
| **Excessive Resource Consumption** | **PARTIAL**: Loop caps (`6` iterations / `6400` planning tokens) exist on `AgentWorkflowState`, **but** `PlatformConfig` overrides are ignored, `AGENT_RUN_TIMEOUT_SECONDS=90` is unimplemented, and `POST /agents/runs` awaits synchronously (`5 req/min` IP rate limit on `:8000` only; `:8006` unprotected). | Unbounded LLM HTTP latencies, retry storms, and real API cost exhaustion (`LLM_API_KEY`) unless per-run timeout, real token accounting, and worker queue backpressure are wired. |
| **Prompt Injection at Integration Boundaries** | **DORMANT (`SIMULATED`)**: `DeterministicMockLLMAdapter` completely ignores `state.prompt_summary` and market text (`graph.py:22-55`), so prompt injection cannot steer tool selection today. | **HIGH**: Malicious `prompt_summary` or poisoned upstream metadata could hijack external LLM planner tool choices or narrative framing without strict prompt separation & schema validation. |
| **Untrusted Market Data** | Tool handlers pull seeded/ingested Data Plane values; fallback static price arrays (`runtime.py:453,466,480,492`) mask missing ClickHouse data silently. | Poisoned market records or extreme spikes entering LLM context could skew narrative summaries if validation/sanitization is missing. |
| **Report Manipulation** | `ReportValidator` checks only `invocation_id` membership (`validator.py:29-30`); `generate_analysis_report` accepts any arbitrary dict from `_llm.synthesize_narrative()` and writes `runtime.reports[run_id]`. | External LLM could fabricate numeric values inside `summary` while attaching valid `invocation_id`s, or inject malicious Markdown/HTML into UI viewers. |
| **Sensitive Data Disclosure** | `AS-IS` evidence contains public spot prices only; `limitations_disclaimer` discloses `adapter=mock`. No secrets live in `evidence_trail`. | **MEDIUM**: Proprietary `prompt_summary` strategies sent to external LLM APIs, or accidental logging of `LLM_API_KEY` / Postgres DSNs. |
| **Tool Side Effects** | **ACTIVE MEDIUM/HIGH GAP**: `detect_anomalies` mutates `anomaly_detector._cooldown_registry` (900s suppression DoS against real alerts!) and appends to `runtime.detected_anomalies`; `generate_analysis_report` writes `runtime.reports` without `is_read_only_market_data=False` or human approval gate. | External LLM repeatedly calling `detect_anomalies` could exhaust cooldown windows and suppress genuine anomaly detection across Plane A/B! |
| **LLM Provider Compromise** | **NOT APPLICABLE (`AS-IS`)**: Zero external LLM network calls or SDKs present. | Compromised third-party LLM endpoint returning malicious tool JSON, poisoned narratives, or experiencing outage/exfiltration. |

## 3. Building Blocks: Required Security Controls

Capability-level threat scenarios, security requirements, authorization matrix, and side-effect approval rules live in:

- [threat-model.md](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/threat-model.md) (`CAP-INT-ORC-TM-001`)
- [security-requirements.md](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/security-requirements.md) (`CAP-INT-ORC-SEC-001`)
- [authorization-matrix.yaml](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/authorization-matrix.yaml)
- [side-effect-and-approval-policy.md](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/side-effect-and-approval-policy.md) (`CAP-INT-ORC-POL-001`)

