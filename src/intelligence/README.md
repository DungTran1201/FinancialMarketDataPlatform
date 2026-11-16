# Intelligence Subsystem (`src/intelligence/`)

Owns **Plane C (Intelligence Plane)**: bounded quantitative investigation orchestration, deterministic tool mediation, workflow state tracking, and citation provenance validation (`ADR-OVR-003` / `ADR-INT-0001`).

> **Documentation Index**: See [docs/intelligence-plane/README.md](../../docs/intelligence-plane/README.md) for full architecture, tool contracts, threat model, and `AS-IS` vs `TARGET` gap tracking.

## Subpackages

| Directory / File | Responsibility | `AS-IS` Reality & Key Invariants |
|---|---|---|
| `orchestrator/graph.py` | `MarketIntelligenceGraph` and `DeterministicMockLLMAdapter` | Executes a pure Python 5-node `while` loop (`zero langgraph imports`); mock LLM plans 7 fixed tools (`420` tokens) and formats deterministic narrative (`540` tokens) inline inside FastAPI `PlatformRuntimeContainer`. |
| `workflows/investigation.py` | `WORKFLOW_NODES` and `AgentWorkflowState` | Tracks step transitions, `max_iterations=6`, and planning ceiling `0.8 * token_budget`; state resides in process memory (`runtime.agent_runs`), not PostgreSQL. |
| `tools/contracts.py`, `tools/gateway.py` | `ApprovedAgentTool`, `ToolGovernancePolicy`, `ControlledToolGateway` | Enforces 10-tool whitelist, RBAC scope check (over hardcoded `_agent_permissions` `AS-IS`), positive row/period caps, `asyncio.wait_for` timeouts, and UUIDv4 provenance. Note: `generate_analysis_report` writes `runtime.reports` and `detect_anomalies` mutates cooldown/anomaly state despite `is_read_only_market_data=True` default. |
| `reporting/validator.py` | `ReportValidator` and `ReportProvenanceError` | Verifies non-empty `provenance_citations` and `invocation_id` membership in `evidence_trail` (does not cross-check numeric values in narrative prose `AS-IS`). |
| `main.py` | `agent-worker` container entrypoint | **`AS-IS` Stub**: Logs `PlatformConfig` parameters and exits immediately (`PostgreSQL` queue polling and Kafka `market.anomalies.v1` consumer are `NOT_IMPLEMENTED`). |
