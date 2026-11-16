---
doc_id: CAP-INT-ORC-AGENT-001
title: "Agent Specification: Market Intelligence Agent"
doc_type: specification
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/intelligence/tools/contracts.py"
related_docs:
  - CAP-INT-ORC-DOC-001
  - INT-ARCH-LLM-001
  - INT-ARCH-EVAL-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Authored Agent Specification per GOV-STD-AGENT-001 covering runtime, tools, loop bounds, memory, and evals."
---

# Agent Specification: Market Intelligence Agent

1. **Agent Identity & Role**: Quantitative Market Investigation Agent (`MarketIntelligenceGraph`), synthesizing structured market reports for monitored crypto spot symbols.
2. **Model Adapter (`AS-IS` vs `TARGET`)**: `DeterministicMockLLMAdapter` (`AS-IS`, `420` plan + `540` synth tokens, ignores `prompt_summary`); external LLM adapter (`TARGET`, behind `ModelAdapterPort`).
3. **Loop & Budget Bounds**: `max_iterations = 6`, `token_budget = 8000` (planning stops at `80%` = `6400`), early exit when `len(evidence_trail) >= 3`.
4. **Authorized Tools**: 10 tools in [tool-contracts.yaml](../../../../../shared-contracts/tool-contracts.yaml). Tools 1–7, 9 are read-only; Tool 8 (`detect_anomalies`) has stateful side effects; Tool 10 (`generate_analysis_report`) is write-capable.
5. **Memory & Persistence**: Ephemeral per-run `AgentWorkflowState` in `runtime.agent_runs` (`AS-IS`); PostgreSQL `agent_runs` + `agent_tool_invocations` (`TARGET`).
6. **Verification & Safety**: `ReportValidator.validate_report()` checks `invocation_id` citations (`AS-IS`); numeric consistency checking and prompt-injection eval harness are `TARGET` (`NOT_IMPLEMENTED`).
