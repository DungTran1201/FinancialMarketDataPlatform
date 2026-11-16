---
doc_id: DIAG-INT-ORC-SEQ-001
title: "Agent Run Sequence Diagram"
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
    - "docs/intelligence-plane/domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/use-cases/uc-int-001-execute-on-demand-investigation.md"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - CAP-INT-ORC-UC-001
  - CAP-INT-ORC-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created Agent Run Sequence Diagram showing AS-IS synchronous await and TARGET async worker."
---

# Agent Run Sequence Diagram

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-SEQ-001` |
| **Purpose** | Illustrate end-to-end runtime sequence for `UC-INT-001` (`AS-IS` inline vs `TARGET` worker). |
| **Scope & Owner** | `capability` (`CAP-INT-ORC-001`) / `ai-engineer` |
| **Authoritative Source** | [uc-int-001-execute-on-demand-investigation.md](../use-cases/uc-int-001-execute-on-demand-investigation.md) (`CAP-INT-ORC-UC-001`) |
| **Notation** | Mermaid `sequenceDiagram` (UML 2.5.1) |
| **Version & Status** | `2.0.0` / `DRAFT` (`SIMULATED`) |

```mermaid
sequenceDiagram
    participant API as "FastAPI Agent Router (Plane B)"
    participant RT as "PlatformRuntimeContainer"
    participant GR as "MarketIntelligenceGraph"
    participant LLM as "DeterministicMockLLMAdapter"
    participant GW as "ControlledToolGateway"
    participant VAL as "ReportValidator"

    API->>RT: execute_agent_investigation(symbol, prompt, idempotency_key)
    RT->>RT: Check idempotency_keys & store AgentWorkflowState (QUEUED)
    RT->>GR: await run_investigation(state)
    GR->>GR: Node 1 intake_and_guardrail_node (RUNNING)
    GR->>LLM: Node 2 plan_tool_sequence(state)
    LLM-->>GR: 7 planned_tools + 420 tokens
    loop For each planned tool
        GR->>GW: Node 3 execute_tool(tool, params, _agent_permissions)
        GW-->>GR: ToolExecutionEnvelope (SUCCESS + provenance)
    end
    GR->>GR: Node 4 evidence_verifier_node (len >= 3 -> break)
    GR->>LLM: Node 5 synthesize_narrative(state)
    LLM-->>GR: report dict + 540 tokens
    GR->>VAL: validate_report(report, evidence_trail)
    VAL-->>GR: True
    GR->>GW: execute_tool("generate_analysis_report", report)
    GW-->>GR: Envelope (persisted in runtime.reports)
    GR-->>RT: completed_state (COMPLETED)
    RT-->>API: (AgentRunTicket, completed_state)
```

**Legend**: Solid arrows (`->>`) represent `AS-IS` synchronous/awaited in-process calls.

