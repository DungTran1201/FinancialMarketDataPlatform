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
  - INT-DOM-ORC-001
  - INT-QA-PLAN-001
  - CAP-INT-ORC-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Completed Intelligence Plane documentation index across architecture, shared tool/data contracts, operations, domain, and CAP-INT-ORC-001 capability artifacts."
---

# Intelligence Plane — Market Investigation Workflow & Tool Gateway

**Scope**: Autonomous quantitative market investigation workflow (`src/intelligence/`), strict 10-tool deterministic gateway (`ControlledToolGateway`), iteration/token loop guardrails, citation ID checking (`ReportValidator`), and target isolated worker/Postgres state contracts.

> [!IMPORTANT]
> **`AS-IS` Simulation & Runtime Disclosure**: Despite module docstrings referencing LangGraph and PostgreSQL checkpoints, `MarketIntelligenceGraph` executes a pure Python `while` loop (`src/intelligence/` has zero `langgraph` imports) driven by `DeterministicMockLLMAdapter` (`LLM_PROVIDER=mock`), runs synchronously inline inside FastAPI `POST /api/v1/agents/runs`, and stores state in memory only (`src/intelligence/main.py` logs config and exits immediately).

## 1. Architecture, Shared Contracts & Operations

- [architecture/README.md](architecture/README.md) (`INT-ARCH-ROOT-001`) — Plane architecture viewpoints (runtime, model integration, tool gateway, security, evaluation), ADRs, and C4/dependency/boundary diagrams.
- [shared-contracts/README.md](shared-contracts/README.md) (`INT-CTR-ROOT-001`) — Canonical [tool-contracts.yaml](shared-contracts/tool-contracts.yaml) (10-tool schema & side-effect registry) and [data-contract.yaml](shared-contracts/data-contract.yaml) (workflow state & persistence contracts).
- **Operations**: [runbook.md](operations/runbook.md) (`INT-OPS-RUN-001`), [incident-and-recovery.md](operations/incident-and-recovery.md) (`INT-OPS-INC-001`), [observability-and-slo.md](operations/observability-and-slo.md) (`INT-OPS-SLO-001`), [test-plan.md](operations/test-plan.md) (`INT-QA-PLAN-001`).

## 2. Domains & Capabilities

| Domain | Capability ID | Capability | Risk Tier | `AS-IS` Status |
|---|---|---|---|---|
| [agent-orchestration-and-tools](domains/agent-orchestration-and-tools/README.md) | `CAP-INT-ORC-001` | [Market Intelligence Workflow & Tool Gateway](domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/README.md) | `HIGH_CRITICAL` | `SIMULATED` |
