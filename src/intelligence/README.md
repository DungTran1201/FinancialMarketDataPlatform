# Intelligence Subsystem (`src/intelligence/`)

Owns **Plane C (Isolated Agentic Intelligence)**: read-only quantitative investigation orchestration, governance policies, workflow state machines, and provenance-enforced report validation (`ADR-006`).

## Subpackages

| Directory | Responsibility | Key Invariants |
|---|---|---|
| `orchestrator/` | `MarketIntelligenceGraph` and `DeterministicMockLLMAdapter` | Drives structured 5-node analytical execution. |
| `workflows/` | `WORKFLOW_NODES` and `AgentWorkflowState` | Tracks step transitions and collected evidence envelopes. |
| `tools/` | `ApprovedAgentTool`, `ToolGovernancePolicy`, and `ControlledToolGateway` (`BR-004`, `CTRL-001`) | Whitelist-only, read-only tool dispatch, RBAC, and bounded row limits. |
| `reporting/` | `ReportValidator` and `ReportProvenanceError` (`CTRL-002`) | Rejects reports citing unverified or fabricated `invocation_id`s. |
| `main.py` | `agent-worker` background service entrypoint | Polls control queue & writes provenance-audited reports. |

