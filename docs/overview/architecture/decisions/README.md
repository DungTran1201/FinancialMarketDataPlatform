---
doc_id: OVR-ADR-ROOT-001
title: "Platform Cross-Plane Architecture Decision Records Index"
doc_type: index
plane: platform
scope_level: platform
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/overview/architecture/decisions/README.md"
related_docs:
  - OVR-ROOT-001
  - ADR-OVR-001
  - ADR-OVR-002
  - ADR-OVR-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Indexed cross-plane ADRs separating verified structural constraints from unresolved monolith-vs-microservices decisions."
---

# Platform Architecture Decision Records (ADRs)

Per [architecture-standards.md](../../../governance/standards/architecture-standards.md), unapproved decisions or unresolved legacy conflicts remain `DRAFT` (`[OPEN]` / `[PROPOSED]`) until human owner sign-off.

| ADR ID | Decision Title | Doc Status | Runtime Reality | Summary |
|---|---|---|---|---|
| `ADR-OVR-001` | [Three-Plane Ownership & DAG Isolation Boundaries](adr-0001-three-plane-ownership-boundaries.md) | `IN_REVIEW` | `IMPLEMENTED` (AST tests pass) | Partitions shared kernel, Data Plane, Application Plane, and Intelligence Plane with enforced acyclic imports. |
| `ADR-OVR-002` | [Modular Monolith vs. Standalone Microservices Runtime](adr-0002-modular-monolith-vs-microservices-runtime.md) | `DRAFT` (`OPEN`) | `PARTIALLY_IMPLEMENTED` (conflicting legacy ADRs) | Captures unresolved conflict between single-process monolith (`main.py`) and 7 isolated container wrappers (`services/*.py`). |
| `ADR-OVR-003` | [Fixed-Point Decimal Precision & Deterministic Tool Gateway](adr-0003-decimal-precision-and-deterministic-tool-gateway.md) | `IN_REVIEW` | `IMPLEMENTED` | Mandates `Decimal` pricing and prohibits raw LLM SQL execution or prompt arithmetic across all planes. |
