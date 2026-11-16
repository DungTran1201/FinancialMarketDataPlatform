---
doc_id: DIAG-INT-ORC-SEQ-001
title: "Sequence Diagram: Agent Investigation Run (AS-IS Inline vs TARGET Worker)"
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
    - "docs/intelligence-plane/architecture/agent-runtime-architecture.md"
related_docs:
  - CAP-INT-ORC-UC-001
  - INT-ARCH-RT-001
  - DIAG-APP-AGT-SEQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Rendered end-to-end investigation sequence showing AS-IS synchronous inline execution inside PlatformRuntimeContainer."
---

# Sequence Diagram: Agent Investigation Run (`AS-IS` Inline vs `TARGET` Worker)

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-SEQ-001` |
| **Title & Purpose** | Chronological sequence of `execute_agent_investigation()` through 5 workflow nodes, gateway tools, and validator |
| **Owner Role & Scope** | `ai-engineer / CAP-INT-ORC-001` |
| **Authoritative Source** | [uc-int-001-execute-on-demand-investigation.md](../use-cases/uc-int-001-execute-on-demand-investigation.md) (`CAP-INT-ORC-UC-001`) |
| **Notation** | `Mermaid sequenceDiagram` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
sequenceDiagram
    autonumber
    participant APP as Application Plane (agent_api)
    participant RT as PlatformRuntimeContainer
    participant GR as MarketIntelligenceGraph
    participant LLM as DeterministicMockLLMAdapter
    participant GW as ControlledToolGateway
    participant VAL as ReportValidator

    APP->>RT: execute_agent_investigation(symbol, prompt, idempotency_key)
    alt idempotency_key already indexed
        RT-->>APP: Return cached (AgentRunTicket, AgentWorkflowState)
    else New Investigation Run
        RT->>RT: Create AgentWorkflowState(QUEUED) in runtime.agent_runs
        RT->>GR: await run_investigation(state) [AS-IS Inline Sync Await]
        GR->>GR: Node 1: intake_and_guardrail_node (symbol allowlist)
        GR->>LLM: Node 2: plan_tool_sequence(state) -> 7 tools, 420 tokens
        loop For each of 7 planned tools (Node 3)
            GR->>GW: await execute_tool(tool, params, _agent_permissions)
            GW-->>GR: ToolExecutionEnvelope(SUCCESS, provenance UUIDv4)
        end
        GR->>GR: Node 4: evidence_verifier_node (len >= 3 -> break)
        GR->>LLM: Node 5: synthesize_narrative(state) -> report dict, 540 tokens
        GR->>VAL: validate_report(report, evidence_trail)
        VAL-->>GR: True (all citation invocation_ids in evidence_trail)
        GR->>GW: await execute_tool("generate_analysis_report", report)
        GW->>RT: Write StructuredAnalysisReport to runtime.reports[run_id]
        GW-->>GR: ToolExecutionEnvelope #8
        GR-->>RT: AgentWorkflowState(status="COMPLETED")
        RT-->>APP: (AgentRunTicket, state) -> Router returns HTTP 202
    end
```

## 3. Legend

- **Inline Synchronous Await**: Step 4 blocks the FastAPI `POST /api/v1/agents/runs` coroutine until Node 5 completes; `TARGET` decouples queuing from `agent-worker` execution.

