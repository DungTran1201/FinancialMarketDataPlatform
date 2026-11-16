---
doc_id: INT-ARCH-RT-001
title: "Agent Runtime & State Architecture"
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
    - "src/intelligence/main.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Documented 5-node pure Python workflow loop, hardcoded catalog check, and idle worker entrypoint."
---

# Agent Runtime & State Architecture

## 1. Scope & Context (`AS-IS` Loop vs `TARGET` LangGraph Worker)

- **State Schema (`AgentWorkflowState`, `investigation.py:19-43`)**: Holds `run_id`, `trigger_mode` (`ON_DEMAND | EVENT_TRIGGERED`), `symbol`, `prompt_summary`, `max_iterations=6`, `token_budget=8000`, `current_iteration`, `tokens_consumed`, `planned_tools`, `evidence_trail`, `visited_nodes`, `final_report`, `status`.
- **Control Method**: `can_continue_planning()` returns `True` iff `current_iteration < max_iterations` AND `tokens_consumed < int(token_budget * 0.8)` (`6400`) AND `status == "RUNNING"`.
- **Graph Library Reality**: Zero `langgraph` imports exist in `src/intelligence/`. `agent-worker` entrypoint (`src/intelligence/main.py`) exits immediately after logging initialization.

## 2. Building Blocks & Runtime Anomalies (`AS-IS`)

1. **Static Monitored Symbol List**: `MarketIntelligenceGraph` hardcodes `("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT")`; dynamic instruments registered in Application Catalog fail Node 1 unless manually synchronized.
2. **Unconnected Config Bounds**: `PlatformRuntimeContainer.execute_agent_investigation()` constructs `AgentWorkflowState()` with defaults `(6, 8000)`, ignoring `PlatformConfig.agent_max_iterations`/`agent_max_tokens_per_run` and `AGENT_RUN_TIMEOUT_SECONDS=90` (unloaded in `settings.py`).
3. **Post-Budget Node 5 Execution**: `report_synthesizer_node` runs outside `while state.can_continue_planning()` and consumes `540` tokens regardless of remaining budget; if `evidence_trail` is empty, `ReportValidator` throws an unhandled `ReportProvenanceError`.
