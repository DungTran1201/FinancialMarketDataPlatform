---
doc_id: INT-ARCH-SEC-001
title: "Agent Security Architecture"
doc_type: architecture
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/tools/contracts.py"
    - "src/serving/api/modules/agent_api/presentation/router.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - INT-ARCH-GW-001
  - CAP-INT-ORC-TM-001
  - CAP-INT-ORC-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Documented trust boundaries and 11 security threat vectors, separating active AS-IS gaps from TARGET external-LLM risks."
---

# Agent Security Architecture

Detailed capability threat model and controls live in [threat-model.md](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/threat-model.md) (`CAP-INT-ORC-TM-001`) and [authorization-matrix.yaml](../domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/security/authorization-matrix.yaml).

## 1. Trust Boundaries

1. **Boundary B1 (Application Plane -> Intelligence Plane)**: `POST /api/v1/agents/runs` (`CAP-APP-AGT-001`) triggers `PlatformRuntimeContainer.execute_agent_investigation()`.
2. **Boundary B2 (Orchestrator -> LLM Adapter)**: `MarketIntelligenceGraph` passes `AgentWorkflowState` to `DeterministicMockLLMAdapter` (`AS-IS`) or external LLM (`TARGET`).
3. **Boundary B3 (Orchestrator -> ControlledToolGateway)**: Tool calls must pass whitelist, permission, and row-limit checks.
4. **Boundary B4 (Tool Gateway -> Data Plane / App Runtime Stores)**: Injected handlers access Redis/ClickHouse/runtime state.

## 2. Threat Matrix (`AS-IS` Active Risks vs. `TARGET` External-LLM Risks)

| Threat Category | Applicability (`AS-IS` vs `TARGET`) | Current Control / Evidence | Identified Gap / Risk |
|---|---|---|---|
| **Unauthorized Agent Invocation** | **Active (`AS-IS`)** | Edge WAF/rate limiter in Plane B | `POST /api/v1/agents/runs` has no route-level RBAC `Depends` check; any caller reaching the API can trigger runs (`SEC-AUDIT-003`). |
| **Privilege Escalation & Hardcoded Permissions** | **Active (`AS-IS`)** | `ControlledToolGateway` checks `granted_permissions` | `MarketIntelligenceGraph` hardcodes `_agent_permissions = {"market:read", "historical:read", "analytics:read", "agent:trigger"}` regardless of caller role. |
| **Tool Abuse (Arbitrary SQL / Unlisted Tools)** | **Mitigated (`AS-IS`)** | `ApprovedAgentTool` enum whitelist | Gateway rejects non-whitelisted tools (`UnauthorizedToolAccessError`); no raw SQL tool exists. |
| **Excessive Resource Consumption** | **Partially Mitigated (`AS-IS`)** | `can_continue_planning()` (`max_iterations=6`, 80% token cap) + per-tool `max_rows_or_periods` | `AGENT_RUN_TIMEOUT_SECONDS=90` is unimplemented; negative `limit` values are not blocked; Node 5 runs post-budget. |
| **Prompt Injection at Integration Boundaries** | **Dormant `AS-IS` / Critical `TARGET`** | `DeterministicMockLLMAdapter` ignores `prompt_summary` | When external LLM is enabled, `prompt_summary` and market string fields become live prompt-injection vectors. |
| **Untrusted Market Data** | **Partially Mitigated (`AS-IS`)** | `Decimal` prices & deterministic math | Handlers fallback to synthetic default price lists when ClickHouse is empty (`runtime.py:453,466,480`), which could mislead callers if mistaken for live data. |
| **Report Manipulation** | **Active (`AS-IS`)** | `ReportValidator` checks `invocation_id` membership | `generate_analysis_report` can overwrite `runtime.reports[run_id]` if invoked directly with an existing `run_id`; prose numbers are not verified. |
| **Sensitive Data Disclosure** | **Low `AS-IS` / High `TARGET`** | No secrets in `AgentWorkflowState`; internal endpoints masked | External LLM integration (`TARGET`) risks leaking internal topology/PII if prompts are not redacted. |
| **Tool Side Effects** | **Active (`AS-IS`)** | Policy table exists | `generate_analysis_report` mutates `runtime.reports` with `is_read_only_market_data=True`; `detect_anomalies` mutates `runtime.detected_anomalies` without human approval or idempotency key. |
| **LLM Provider Compromise** | **Dormant `AS-IS` / High `TARGET`** | Offline mock adapter | Compromised external model could attempt tool-argument manipulation or biased narratives (`TARGET`). |

