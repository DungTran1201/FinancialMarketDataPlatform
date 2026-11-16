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
  - INT-QA-PLAN-001
  - CAP-INT-ORC-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created Intelligence Plane documentation root covering 5-node Python loop, DeterministicMockLLMAdapter, ControlledToolGateway, and provenance validation."
---

# Intelligence Plane — Market Investigation Workflow & Tool Gateway

**Scope**: Autonomous quantitative market investigation workflow (`src/intelligence/`), strict 10-tool deterministic gateway (`ControlledToolGateway`), iteration/token loop guardrails, zero-hallucination citation checking (`ReportValidator`), and target isolated worker/Postgres state contracts.

> [!IMPORTANT]
> **`AS-IS` Simulation & Runtime Disclosure**: Despite module docstrings referencing LangGraph and PostgreSQL checkpoints, `MarketIntelligenceGraph` executes a pure Python `while` loop (`src/intelligence/` has zero `langgraph` imports) driven by `DeterministicMockLLMAdapter` (`LLM_PROVIDER=mock`), runs synchronously inline inside FastAPI `POST /api/v1/agents/runs`, and stores state in memory only (`src/intelligence/main.py` logs config and exits immediately).

## 1. Architecture, Shared Tool Contracts & Operations

- [architecture/README.md](architecture/README.md) (`INT-ARCH-ROOT-001`) — Runtime, LLM integration, tool gateway, security, evaluation, ADRs, and diagrams.
- [shared-contracts/README.md](shared-contracts/README.md) (`INT-CTR-ROOT-001`) and [shared-contracts/tool-contracts.yaml](shared-contracts/tool-contracts.yaml) — Authoritative 10-tool policy registry.
- [operations/runbook.md](operations/runbook.md), [incident-and-recovery.md](operations/incident-and-recovery.md), [observability-and-slo.md](operations/observability-and-slo.md), [test-plan.md](operations/test-plan.md).

## 2. Domains & Capabilities

| Domain | Capability ID | Capability | Risk Tier | `AS-IS` Status |
|---|---|---|---|---|
| [agent-orchestration-and-tools](domains/agent-orchestration-and-tools/README.md) | `CAP-INT-ORC-001` | [Market Intelligence Workflow & Tool Gateway](domains/agent-orchestration-and-tools/capabilities/market-intelligence-workflow-and-tool-gateway/README.md) | `HIGH_CRITICAL` | `SIMULATED` |
