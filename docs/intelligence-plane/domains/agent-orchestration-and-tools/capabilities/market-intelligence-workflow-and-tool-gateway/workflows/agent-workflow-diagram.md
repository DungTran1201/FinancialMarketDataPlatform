---
doc_id: DIAG-INT-ORC-AGT-001
title: "Agent Workflow & Tool-Guard Diagram: 5-Node MarketInvestigationGraph"
doc_type: diagram
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/design/agent-specification.md"
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/workflows/workflow-specification.md"
related_docs:
  - CAP-INT-ORC-AGT-001
  - CAP-INT-ORC-WF-001
  - INT-ARCH-RT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Rendered 5-node pure Python workflow loop, budget checks, ControlledToolGateway guards, and ReportValidator gate."
---

# Agent Workflow & Tool-Guard Diagram: 5-Node `MarketIntelligenceGraph`

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-AGT-001` |
| **Title & Purpose** | Execution graph for `MarketIntelligenceGraph.run_investigation()` with budget, tool-gateway, and provenance checks |
| **Owner Role & Scope** | `ai-engineer / CAP-INT-ORC-001` |
| **Authoritative Source** | [agent-specification.md](../design/agent-specification.md) (`CAP-INT-ORC-AGT-001`) |
| **Notation** | `Mermaid flowchart TD` (`Agent Execution Graph`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
flowchart TD
    start(["Entry: AgentWorkflowState (status=QUEUED)"])
    n1["Node 1: intake_and_guardrail_node"]
    g_sym{"Symbol in _monitored_symbols?"}
    fail_sym(["Return status=FAILED (final_report=error)"])
    g_budget{"can_continue_planning(): iter < 6 AND tokens < 6400?"}
    n2["Node 2: investigation_planner_node (MockLLM AS-IS)"]
    g_plan{"planned_tools non-empty?"}
    n3["Node 3: tool_gateway_executor_node"]
    gw_chk{"ControlledToolGateway: Whitelist + RBAC + Limit + Timeout"}
    err_unhandled(["Unhandled Exception (Stuck in RUNNING AS-IS)"])
    n4["Node 4: evidence_verifier_node"]
    g_ev{"len(evidence_trail) >= 3?"}
    n5["Node 5: report_synthesizer_node (Outside Budget Guard)"]
    val_chk{"ReportValidator: Non-empty & Valid invocation_id?"}
    persist["Tool #10: generate_analysis_report (Writes runtime.reports)"]
    done(["Exit: status=COMPLETED"])

    start --> n1 --> g_sym
    g_sym -->|"No"| fail_sym
    g_sym -->|"Yes (status=RUNNING)"| g_budget
    g_budget -->|"True"| n2 --> g_plan
    g_budget -->|"False"| n5
    g_plan -->|"Empty []"| n5
    g_plan -->|"Tools Selected"| n3 --> gw_chk
    gw_chk -.->|"Unauthorized / Limit / Timeout"| err_unhandled
    gw_chk -->|"Append Envelope"| n4 --> g_ev
    g_ev -->|"len < 3"| g_budget
    g_ev -->|"len >= 3"| n5
    n5 --> val_chk
    val_chk -.->|"ReportProvenanceError"| err_unhandled
    val_chk -->|"Valid Citations"| persist --> done
```

## 3. Legend

- **Rounded Pill (`([...])`)**: Workflow entry, terminal status (`COMPLETED`, `FAILED`), or `AS-IS` unhandled exception exit.
- **Diamond (`{...}`)**: Deterministic branch condition, loop budget guard, tool gateway firewall, or provenance check.
- **Solid vs Dashed Arrows**: Implemented control-flow transitions (`-->`) vs unhandled failure propagation paths (`-.->`).

