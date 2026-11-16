---
doc_id: INT-ARCH-001
title: "Intelligence Plane Architecture Description"
doc_type: architecture
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-RT-001
  - INT-ARCH-GW-001
  - DIAG-INT-C4-001
  - ADR-INT-0001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented Intelligence Plane scope, 5-node building blocks, deterministic gateway isolation, and key gaps."
---

# Intelligence Plane Architecture Description

## 1. Scope & Context

The **Intelligence Plane (Plane C)** synthesizes human-readable, citation-grounded market investigation reports by orchestrating quantitative deterministic tools over normalized financial stores without ever permitting free-form LLM SQL generation or floating-point arithmetic (`ADR-0003`).

```
  Application Plane (CAP-APP-AGT-001)
     │  POST /api/v1/agents/runs (sync await inside API handler AS-IS)
     ▼
  MarketIntelligenceGraph (5-node async loop, pure Python)
     ├── Node 1: intake_and_guardrail_node  (monitored symbol allowlist)
     ├── Node 2: investigation_planner_node (DeterministicMockLLMAdapter AS-IS)
     ├── Node 3: tool_gateway_executor_node ──▶ ControlledToolGateway (10 approved tools)
     ├── Node 4: evidence_verifier_node     (stops when >= 3 evidence envelopes)
     └── Node 5: report_synthesizer_node    ──▶ ReportValidator + Tool #10 (generate_analysis_report)
```

## 2. Building Blocks & Verified Architectural Gaps

- **Isolated Execution Gap**: `src/intelligence/main.py` logs worker settings and exits; real investigations run inside `PlatformRuntimeContainer.execute_agent_investigation()` rather than an asynchronous worker queue consuming Postgres `agent_runs`.
- **LLM Integration**: External LLM SDKs (`OpenAI`/`Anthropic`/`Gemini`) are absent (`LLM_PROVIDER=mock`); `DeterministicMockLLMAdapter` emits fixed 7-tool plans (`420` tokens) and report summaries (`540` tokens).
- **Tool Write Side Effects**: Contrary to read-only framing, `generate_analysis_report` mutates `runtime.reports[run_id]` (while defaulting `is_read_only_market_data=True`), and `detect_anomalies` appends directly to `runtime.detected_anomalies`.
- **Validation Limits**: `ReportValidator.validate_report()` checks non-empty `provenance_citations` and `invocation_id` membership only; it does not cross-check numeric values inside narrative `summary` text.
