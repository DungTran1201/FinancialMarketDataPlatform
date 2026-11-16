# Intelligence Subsystem (`src/intelligence/`)

Owns **Plane C (Intelligence Plane)**: quantitative market investigation orchestration, workflow state schema, deterministic `ControlledToolGateway` mediation, and citation provenance validation (`ADR-INT-0001`, `ADR-OVR-003`).

> **`AS-IS` Runtime Note**: `MarketIntelligenceGraph` executes a pure Python `while` loop (no `langgraph` imports) using `DeterministicMockLLMAdapter`, invoked synchronously inline by `PlatformRuntimeContainer.execute_agent_investigation()` with in-memory state. `main.py` (`agent-worker`) currently logs configuration and exits without polling PostgreSQL or Kafka.

## Subpackages

| Directory | Responsibility | Key Invariants |
|---|---|---|
| `orchestrator/` | `MarketIntelligenceGraph` and `DeterministicMockLLMAdapter` | Drives 5-node investigation loop (`AS-IS` pure Python + mock LLM). |
| `workflows/` | `WORKFLOW_NODES` and `AgentWorkflowState` | Tracks step transitions, `can_continue_planning()` budgets, and `evidence_trail`. |
| `tools/` | `ApprovedAgentTool`, `APPROVED_TOOL_POLICIES`, and `ControlledToolGateway` | Whitelist-only 10-tool dispatch, RBAC, row limits, `asyncio.wait_for` timeouts, and in-memory `_audit_log`. |
| `reporting/` | `ReportValidator` and `ReportProvenanceError` | Rejects reports with empty citations or fabricated `invocation_id`s. |
| `main.py` | `agent-worker` CLI entrypoint | Logs `PlatformConfig` agent settings and exits (`AS-IS` stub). |
