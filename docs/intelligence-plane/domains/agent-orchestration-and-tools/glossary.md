---
doc_id: INT-DOM-ORC-GLOSS-001
title: "Domain Glossary: Agent Orchestration & Deterministic Tools"
doc_type: glossary
plane: intelligence-plane
scope_level: domain
domain: agent-orchestration-and-tools
status: DRAFT
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: business-analyst
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/workflows/investigation.py"
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
related_docs:
  - INT-DOM-ORC-001
  - INT-DOM-ORC-SPEC-001
  - OVR-GLOSS-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Defined ubiquitous terminology and disallowed synonyms for agent orchestration and deterministic tool governance."
---

# Domain Glossary: Agent Orchestration & Deterministic Tools

| Term | Code Symbol | Authoritative Definition | Disallowed Synonyms |
|---|---|---|---|
| **Agent Workflow State** | `AgentWorkflowState` (`workflows/investigation.py`) | Mutable per-run state tracking `run_id`, `trigger_mode`, `symbol`, iteration/token counters, `planned_tools`, `evidence_trail`, `visited_nodes`, `final_report`, and `status`. | LangGraph Postgres Checkpoint (`AS-IS` is in-memory only) |
| **Approved Agent Tool** | `ApprovedAgentTool` (`tools/contracts.py`) | Strictly enumerated set of 10 deterministic tools callable via `ControlledToolGateway`. | Arbitrary SQL tool / dynamic plugin |
| **Controlled Tool Gateway** | `ControlledToolGateway` (`tools/gateway.py`) | Security and determinism firewall enforcing tool whitelist, permission checks, row/period caps, timeouts, and provenance wrapping. | Unchecked tool executor |
| **Tool Execution Envelope** | `ToolExecutionEnvelope` (`tools/contracts.py`) | Standardized wrapper containing `status`, `data`, and `ToolProvenanceMetadata`. | Raw JSON dict |
| **Tool Provenance Metadata** | `ToolProvenanceMetadata` (`tools/contracts.py`) | Immutable audit record (`invocation_id`, `tool_name`, `source_store`, `symbol`, `window_start`, `window_end`, `row_count`, `executed_at`). | Generic trace log |
| **Evidence Trail** | `AgentWorkflowState.evidence_trail` | Ordered list of `ToolExecutionEnvelope` records accumulated during a run; authoritative reference set for `ReportValidator`. | Prompt context memory |
| **Report Validator** | `ReportValidator` (`reporting/validator.py`) | Verifies non-empty `provenance_citations` and checks every `invocation_id` exists in `evidence_trail`. | Full semantic / numeric anti-hallucination verifier (`AS-IS` checks ID membership only) |
| **Deterministic Mock LLM Adapter** | `DeterministicMockLLMAdapter` (`orchestrator/graph.py`) | Offline deterministic adapter returning a fixed 7-tool plan and structured summary dict (`LLM_PROVIDER=mock`). | Production OpenAI/LangGraph agent |

