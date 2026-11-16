---
doc_id: INT-ARCH-ROOT-001
title: "Intelligence Plane Architecture Hub"
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
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/intelligence/reporting/validator.py"
    - "src/intelligence/main.py"
related_docs:
  - INT-ROOT-001
  - INT-ARCH-001
  - INT-ARCH-RT-001
  - INT-ARCH-LLM-001
  - INT-ARCH-GW-001
  - INT-ARCH-SEC-001
  - INT-ARCH-EVAL-001
  - INT-ADR-ROOT-001
  - DIAG-INT-C4-001
  - DIAG-INT-DEP-001
  - DIAG-INT-GW-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Indexed all Intelligence Plane architecture viewpoints, ADRs, and Plane-level C4, dependency, and trust-boundary diagrams."
---

# Intelligence Plane Architecture Hub

This hub organizes the Plane-level architecture descriptions, Architecture Decision Records (ADRs), and derived architectural diagrams for the **Intelligence Plane (`Plane C`)**.

## 1. Architecture Viewpoints

| Document | Doc ID | Scope & Focus | `AS-IS` Implementation |
|---|---|---|---|
| [intelligence-architecture.md](intelligence-architecture.md) | `INT-ARCH-001` | Holistic context, scope/ownership, building blocks, dependency DAG, cross-plane contracts, `AS-IS` vs `TARGET` topology, and risks | `SIMULATED` |
| [agent-runtime-architecture.md](agent-runtime-architecture.md) | `INT-ARCH-RT-001` | Entrypoint stub, pure Python 5-node loop vs `TARGET` LangGraph worker, state lifecycle, budgets, timeouts, and recovery | `SIMULATED` |
| [model-integration-architecture.md](model-integration-architecture.md) | `INT-ARCH-LLM-001` | Model adapter interface, `DeterministicMockLLMAdapter` (`AS-IS`), `TARGET` external LLM providers, prompt boundaries, and fallbacks | `SIMULATED` |
| [tool-gateway-architecture.md](tool-gateway-architecture.md) | `INT-ARCH-GW-001` | 10-tool registry, declared vs actual backing stores, validation/RBAC/limits/timeouts, provenance, audit, and write side effects | `PARTIALLY_IMPLEMENTED` |
| [agent-security-architecture.md](agent-security-architecture.md) | `INT-ARCH-SEC-001` | Trust boundaries, hardcoded agent permissions, side-effect risks, and `AS-IS` vs external-LLM threat vectors | `PARTIALLY_IMPLEMENTED` |
| [evaluation-and-observability.md](evaluation-and-observability.md) | `INT-ARCH-EVAL-001` | Provenance citations, `ReportValidator` scope limits, token/latency/error telemetry, numeric consistency gap, and replay | `PARTIALLY_IMPLEMENTED` |

## 2. Decisions & Diagrams

- **ADRs**: [decisions/README.md](decisions/README.md) (`INT-ADR-ROOT-001`) -> [ADR-INT-0001](decisions/adr-0001-deterministic-gateway-over-freeform-sql.md) (Deterministic Tool Gateway over Freeform LLM SQL/Math).
- **C4 Container Diagram**: [diagrams/intelligence-c4-container.md](diagrams/intelligence-c4-container.md) (`DIAG-INT-C4-001` — `AS-IS` in-process monolith wiring vs `TARGET` isolated `agent-worker`).
- **Dependency & Boundary Diagram**: [diagrams/intelligence-dependency-diagram.md](diagrams/intelligence-dependency-diagram.md) (`DIAG-INT-DEP-001` — Clean Architecture AST isolation rules).
- **Tool Gateway Trust Boundary Diagram**: [diagrams/tool-gateway-boundaries.md](diagrams/tool-gateway-boundaries.md) (`DIAG-INT-GW-001` — Whitelist, RBAC, row cap, timeout, and side-effect boundaries).
