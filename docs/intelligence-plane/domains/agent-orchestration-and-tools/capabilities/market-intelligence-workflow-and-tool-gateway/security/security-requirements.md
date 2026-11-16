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
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
    - "src/intelligence/orchestrator/graph.py"
related_docs:
  - CAP-INT-ORC-TM-001
  - INT-ARCH-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Defined security requirements and side-effect/approval policies for CAP-INT-ORC-001."
---

# Security Requirements (`CAP-INT-ORC-001`)

| Sec ID | Requirement | `AS-IS` Status | Linked Threat |
|---|---|---|---|
| `SEC-INT-001` | `ControlledToolGateway` MUST reject any tool not in `ApprovedAgentTool` and enforce `required_permission`. | `IMPLEMENTED` | `THR-INT-001` |
| `SEC-INT-002` | Caller RBAC permissions MUST be propagated from Plane B JWT claims instead of hardcoded `_agent_permissions`. | `NOT_IMPLEMENTED` | `THR-INT-001` |
| `SEC-INT-003` | Write-capable tools (`generate_analysis_report`) and stateful tools (`detect_anomalies`) MUST declare `is_read_only_market_data=False` and enforce idempotency/approval policy. | `PARTIALLY_IMPLEMENTED` (flag defaults `True`) | `THR-INT-002` |
| `SEC-INT-004` | End-to-end run timeout (`AGENT_RUN_TIMEOUT_SECONDS`) MUST be enforced around `run_investigation()`. | `NOT_IMPLEMENTED` | `THR-INT-003` |
| `SEC-INT-005` | `ReportValidator` MUST verify citation IDs (`AS-IS`) and numeric consistency in narrative text (`TARGET`). | `PARTIALLY_IMPLEMENTED` | `THR-INT-004` |
| `SEC-INT-006` | External LLM adapters (`TARGET`) MUST isolate untrusted `prompt_summary` and strip secrets/PII before egress. | `NOT_IMPLEMENTED` (mock adapter offline) | `THR-INT-005` |

## Side-Effect & Human Approval Policy
- **Read-Only Tools (Tools 1–7, 9)**: Autonomous execution permitted within `max_rows_or_periods` and `timeout_seconds`.
- **Stateful Evaluation (`detect_anomalies`)**: Autonomous execution permitted under 900s cooldown; `TARGET` requires separating read-only evaluation from state mutation.
- **Write-Capable (`generate_analysis_report`)**: Autonomous execution permitted **only** at Node 5 after `ReportValidator` passes, keyed strictly by `run_id`; external/destructive write tools remain prohibited without explicit human-in-the-loop approval.

