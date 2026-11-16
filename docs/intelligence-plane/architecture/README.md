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
    summary: "Indexed all Intelligence Plane architecture viewpoints, ADRs, and C4/Dependency/Trust-Boundary diagrams."
---

# Intelligence Plane Architecture Hub

## 1. Architecture Viewpoints

| Document | ID | Focus | `AS-IS` Status |
|---|---|---|---|
| [intelligence-architecture.md](intelligence-architecture.md) | `INT-ARCH-001` | Holistic Intelligence Plane context, boundaries, topology, and gaps | `SIMULATED` |
| [agent-runtime-architecture.md](agent-runtime-architecture.md) | `INT-ARCH-RT-001` | 5-node Python loop, state lifecycle, budgets, timeouts, and stubbed worker | `SIMULATED` |
| [model-integration-architecture.md](model-integration-architecture.md) | `INT-ARCH-LLM-001` | `DeterministicMockLLMAdapter` vs `TARGET` external LLM providers | `SIMULATED` |
| [tool-gateway-architecture.md](tool-gateway-architecture.md) | `INT-ARCH-GW-001` | `ControlledToolGateway` 10-tool registry, RBAC, bounds, audit, side effects | `PARTIALLY_IMPLEMENTED` |
| [agent-security-architecture.md](agent-security-architecture.md) | `INT-ARCH-SEC-001` | Trust boundaries, hardcoded permissions, injection, and write-tool risks | `PARTIALLY_IMPLEMENTED` |
| [evaluation-and-observability.md](evaluation-and-observability.md) | `INT-ARCH-EVAL-001` | `ReportValidator` provenance checks, telemetry, and evaluation gaps | `PARTIALLY_IMPLEMENTED` |

## 2. Decisions & Diagrams

- **Decisions**: [decisions/README.md](decisions/README.md) (`INT-ADR-ROOT-001`) — [ADR-INT-0001](decisions/adr-0001-deterministic-gateway-over-freeform-sql.md).
- **Diagrams**:
  - [diagrams/intelligence-c4-container.md](diagrams/intelligence-c4-container.md) (`DIAG-INT-C4-001`) — C4 Container Diagram.
  - [diagrams/intelligence-dependency-diagram.md](diagrams/intelligence-dependency-diagram.md) (`DIAG-INT-DEP-001`) — Intelligence Plane Dependency Diagram.
  - [diagrams/tool-gateway-boundaries.md](diagrams/tool-gateway-boundaries.md) (`DIAG-INT-GW-001`) — Tool Gateway Trust Boundary Diagram.
