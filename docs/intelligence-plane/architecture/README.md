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
  - DIAG-INT-GW-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Indexed Intelligence Plane architecture viewpoints, ADRs, and C4/Tool-Boundary diagrams."
---

# Intelligence Plane Architecture Hub

## 1. Architecture Viewpoints

- [intelligence-architecture.md](intelligence-architecture.md) (`INT-ARCH-001`) — Holistic Intelligence Plane architecture and boundaries.
- [agent-runtime-architecture.md](agent-runtime-architecture.md) (`INT-ARCH-RT-001`) — 5-node workflow execution engine vs stubbed worker (`src/intelligence/main.py`).
- [model-integration-architecture.md](model-integration-architecture.md) (`INT-ARCH-LLM-001`) — `DeterministicMockLLMAdapter` (`SIMULATED`) vs unimplemented external LLM clients.
- [tool-gateway-architecture.md](tool-gateway-architecture.md) (`INT-ARCH-GW-001`) — `ControlledToolGateway` whitelist, RBAC, row/timeout caps, and side-effect discrepancies.
- [agent-security-architecture.md](agent-security-architecture.md) (`INT-ARCH-SEC-001`) — Prompt injection surface, unauthenticated trigger ingress, and write-tool risks.
- [evaluation-and-observability.md](evaluation-and-observability.md) (`INT-ARCH-EVAL-001`) — `ReportValidator` provenance checks and evaluation harness gaps.

## 2. Decisions & Diagrams

- [decisions/README.md](decisions/README.md) (`INT-ADR-ROOT-001`) — [ADR-INT-0001](decisions/adr-0001-deterministic-gateway-over-freeform-sql.md).
- [diagrams/intelligence-c4-container.md](diagrams/intelligence-c4-container.md) (`DIAG-INT-C4-001`)
- [diagrams/tool-gateway-boundaries.md](diagrams/tool-gateway-boundaries.md) (`DIAG-INT-GW-001`)
