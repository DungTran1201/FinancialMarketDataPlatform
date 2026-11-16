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
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/reporting/validator.py"
related_docs:
  - INT-ARCH-SEC-001
  - CAP-INT-ORC-SEC-001
  - DIAG-INT-ORC-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Authored STRIDE-aligned threat model for CAP-INT-ORC-001 distinguishing AS-IS risks from TARGET external-LLM threats."
---

# Threat Model: `CAP-INT-ORC-001`

Derived diagram: [threat-model-diagram.md](threat-model-diagram.md) (`DIAG-INT-ORC-TM-001`).

| Threat ID | Threat & Vector | Phase | Current Mitigation (`AS-IS`) | Residual Risk / Gap |
|---|---|---|---|---|
| `THR-INT-001` | **Hardcoded Agent Permissions**: `MarketIntelligenceGraph` passes `_agent_permissions` (all 4 scopes) regardless of caller identity. | `AS-IS` | None inside Plane C | Caller with `viewer` role could indirectly trigger `agent:trigger` write if route RBAC is absent (`SEC-AUDIT-003`). |
| `THR-INT-002` | **Unmarked Tool Side Effects**: `generate_analysis_report` (`runtime.reports` write) & `detect_anomalies` (`detected_anomalies` append) lack approval gates and `is_read_only_market_data=False` flag. | `AS-IS` | `agent:trigger` permission on report tool | Direct overwrite of `runtime.reports[run_id]`; anomaly list mutation on `analytics:read`. |
| `THR-INT-003` | **Runaway Loop / Missing Run Timeout**: `AGENT_RUN_TIMEOUT_SECONDS=90` is unimplemented; Node 5 runs post-budget. | `AS-IS` | `can_continue_planning()` (`max_iterations=6`, 80% token cap) + per-tool `wait_for` | Slow external LLM or repeated timeouts could hang inline FastAPI request. |
| `THR-INT-004` | **Shallow Numeric Hallucination Check**: `ReportValidator` only checks `invocation_id` existence. | `AS-IS` / `TARGET` | `ReportProvenanceError` on fabricated IDs | Narrative prose could misquote numbers while citing a valid `invocation_id` (`GAP-INT-006`). |
| `THR-INT-005` | **Prompt Injection & Secret Egress**: Untrusted `prompt_summary` or market strings passed to external LLM. | `TARGET` | Dormant `AS-IS` (`DeterministicMockLLMAdapter` ignores `prompt_summary`) | Must sanitize prompts, isolate system instructions, and redact secrets before enabling external LLM. |

