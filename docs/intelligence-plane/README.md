---
doc_id: INT-ROOT-001
title: "Intelligence Plane — Market Investigation Workflow & Tool Gateway"
doc_type: index
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
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/intelligence/reporting/validator.py"
    - "src/intelligence/main.py"
related_docs:
  - OVR-ROOT-001
  - INT-ARCH-ROOT-001
  - INT-CTR-ROOT-001
  - INT-QA-PLAN-001
  - INT-DOM-ORC-001
  - CAP-INT-ORC-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Completed Intelligence Plane documentation index covering architecture, shared tool/data contracts, domain/capability specs, security, diagrams, and operations."
---

# Intelligence Plane — Market Investigation Workflow & Tool Gateway

**Scope**: Autonomous quantitative market investigation workflow (`src/intelligence/`), strict 10-tool deterministic gateway (`ControlledToolGateway`), iteration/token loop guardrails, citation checking (`ReportValidator`), and target isolated worker/PostgreSQL state contracts.

> [!IMPORTANT]
> **`AS-IS` Simulation & Runtime Disclosure**: Despite module docstrings referencing LangGraph and PostgreSQL checkpoints, `MarketIntelligenceGraph` executes a pure Python `while` loop (`src/intelligence/` has zero `langgraph` imports) driven by `DeterministicMockLLMAdapter` (`LLM_PROVIDER=mock`), runs synchronously inline inside FastAPI `POST /api/v1/agents/runs` via `PlatformRuntimeContainer.execute_agent_investigation()`, and stores state in memory only (`src/intelligence/main.py` logs config and exits immediately).

## 1. Ownership Boundaries

- **Owned by Intelligence Plane**: Agent orchestration & workflow runtime, model adapter abstraction, tool registry & `ControlledToolGateway`, tool authorization & execution bounds, `AgentWorkflowState`, evidence collection & provenance, report synthesis & `ReportValidator`, agent safety/evaluation, and agent execution observability.
- **Explicitly Out of Scope (Referenced via Contracts Only)**:
  - HTTP API Gateway, user authentication, frontend `AiWorkspaceModule`, and `/api/v1/agents` + `/api/v1/reports` endpoints (owned by Application Plane `CAP-APP-AGT-001`).
  - Market data ingestion, Kafka topic schemas (`market.anomalies.v1`), Redis/ClickHouse/MinIO storage (owned by Data Plane).

## 2. Architecture, Shared Contracts & Operations

- [architecture/README.md](architecture/README.md) (`INT-ARCH-ROOT-001`) — Plane architecture, runtime, model integration, tool gateway, security, evaluation, ADRs, and C4/dependency/trust diagrams.
- [shared-contracts/README.md](shared-contracts/README.md) (`INT-CTR-ROOT-001`) — Authoritative [tool-contracts.yaml](shared-contracts/tool-contracts.yaml) (all 10 `ApprovedAgentTool` definitions) and [data-contract.yaml](shared-contracts/data-contract.yaml).
- Operations:
  - [operations/runbook.md](operations/runbook.md) (`INT-OPS-RUN-001`)
  - [operations/incident-and-recovery.md](operations/incident-and-recovery.md) (`INT-OPS-INC-001`)
  - [operations/observability-and-slo.md](operations/observability-and-slo.md) (`INT-OPS-SLO-001`)
  - [operations/test-plan.md](operations/test-plan.md) (`INT-QA-PLAN-001`)

## 3. Domains & Capabilities

| Domain | Capability ID | Capability | Risk Tier | `AS-IS` Status |
|---|---|---|---|---|
| [agent-orchestration-and-tools](domains/agent-orchestration-and-tools/README.md) | `CAP-INT-ORC-001` | [Market Intelligence Workflow & Tool Gateway](domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/README.md) | `HIGH_CRITICAL` | `SIMULATED` |
