---
doc_id: DIAG-INT-ORC-FLOW-001
title: "Agent Workflow Diagram (5-Node Investigation Loop)"
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
    - "docs/intelligence-plane/architecture/agent-runtime-architecture.md"
    - "src/intelligence/orchestrator/graph.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - CAP-INT-ORC-AGENT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created Agent Workflow Diagram matching the 5-node Python loop in MarketIntelligenceGraph."
---

# Agent Workflow Diagram

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-FLOW-001` |
| **Purpose** | Visualize the 5-node execution flow, loop bounds, and early-exit logic in `MarketIntelligenceGraph`. |
| **Scope & Owner** | `capability` (`CAP-INT-ORC-001`) / `ai-engineer` |
| **Authoritative Source** | [agent-runtime-architecture.md](../../../../../architecture/agent-runtime-architecture.md) (`INT-ARCH-RT-001`) |
| **Notation** | Mermaid `flowchart TD` (Agent Execution Graph) |
| **Version & Status** | `2.0.0` / `DRAFT` (`SIMULATED`) |

```mermaid
flowchart TD
    START(["Start: run_investigation(state)"]) --> N1["Node 1: intake_and_guardrail_node"]
    N1 -->|"symbol not in _monitored_symbols"| FAIL(["status = FAILED"])
    N1 -->|"symbol valid -> status = RUNNING"| GUARD{"can_continue_planning()? (iter < 6 & tokens < 6400)"}
    GUARD -->|"True"| N2["Node 2: investigation_planner_node (DeterministicMockLLMAdapter)"]
    N2 -->|"planned_tools empty"| N5["Node 5: report_synthesizer_node"]
    N2 -->|"planned_tools non-empty"| N3["Node 3: tool_gateway_executor_node (ControlledToolGateway)"]
    N3 --> N4["Node 4: evidence_verifier_node"]
    N4 -->|"len(evidence_trail) >= 3"| N5
    N4 -->|"len(evidence_trail) < 3"| GUARD
    GUARD -->|"False (budget/iter cap)"| N5
    N5 -->|"ReportValidator + generate_analysis_report"| DONE(["status = COMPLETED"])
```

**Legend**: Solid edges (`-->`) show `AS-IS` Python control flow; diamond nodes represent conditional loop/guardrail checks.
