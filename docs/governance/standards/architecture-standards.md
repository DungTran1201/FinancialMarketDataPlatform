---
doc_id: GOV-STD-ARCH-001
title: "Architecture Documentation & ADR Standards"
doc_type: standard
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: system-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/standards/architecture-standards.md"
related_docs:
  - GOV-STD-REG-001
  - GOV-STD-DIAG-001
  - GOV-POL-SOT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established arc42-adapted viewpoint rules, MADR 4.0.0 ADR lifecycle, AS-IS vs TARGET separation, and risk/trade-off standards."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Initial Documentation V2 architecture documentation standard."
---

# Architecture Documentation & ADR Standards

Adapts **arc42 (v9.x)**, **C4 Model**, and **MADR 4.0.0** at the appropriate ownership boundary (`Platform Overview`, `Plane`, or `Capability`) instead of creating a single monolithic architecture document.

## 1. Architecture Viewpoints by Scope

| Scope | Required Architecture Viewpoints | Template |
|---|---|---|
| **Platform Overview (`overview/`)** | System Context (C4 L1), Cross-Plane Dependency Matrix, Global Constraints & Quality Goals, Cross-Plane ADRs | `architecture-description.template.md` |
| **Plane (`<plane>/architecture/`)** | Plane Container View (C4 L2), Plane Cross-Cutting Concepts (auth, resilience, observability, storage strategy), Deployment View, Architecture Risks & Trade-Offs | `architecture-description.template.md` |
| **Capability (`<capability>/design/`)** | Component Design (C4 L3 / module boundaries), Runtime Interactions (Sequence/State where applicable), Capability Constraints & Trade-Offs | `component-design.template.md` |

## 2. Mandatory Separation of Current Implementation (`AS-IS`) vs. Target Architecture (`TARGET`)

1. Every architecture or component specification MUST explicitly separate **Current Implementation (`AS-IS`)** from **Target Architecture (`TARGET`)** using dedicated subsections or status badges (`IMPLEMENTED | PARTIALLY_IMPLEMENTED | SIMULATED | NOT_IMPLEMENTED | PLANNED`).
2. `AS-IS` statements MUST cite verified source paths, deployment configs, or test evidence.
3. A `TARGET` design MUST NOT be described as live production behavior merely because an ADR was approved or a Compose service was declared.
4. Any `TARGET` capability lacking code implementation MUST carry `implementation_status: NOT_IMPLEMENTED` or `PLANNED` in frontmatter and `capability.yaml`.

## 3. Architecture Decision Records (MADR 4.0.0)

1. Significant architectural choices (plane boundaries, storage engines, delivery guarantees, protocol choices, authentication models, decomposition choices) MUST be captured in an ADR instantiated from [adr.template.md](../templates/architecture/adr.template.md).
2. ADRs MUST reside at the lowest scope owning all affected components:
   - Cross-plane: `docs/overview/decisions/`
   - Single plane: `docs/<plane>/decisions/`
   - Single capability: `docs/<plane>/domains/<domain>/capabilities/<capability>/decisions/`
3. **Lifecycle States**: An ADR uses document statuses `DRAFT` (proposed/unreviewed), `IN_REVIEW`, `APPROVED` (accepted by accountable architect/owner), or `DEPRECATED` (superseded, with mandatory `superseded_by` reference).
4. **Prohibition**: Unapproved architectural hypotheses MUST remain `DRAFT` (tagged `[PROPOSED]`) and MUST NOT be presented as `APPROVED` decisions.

## 4. Constraints, Dependencies, Quality Attributes & Technical Risks

Every architecture description MUST document:

- **Architecture Constraints**: Technology, regulatory, budget, and clean-dependency boundaries (e.g., module DAG constraints).
- **External & Cross-Plane Dependencies**: Exact upstream/downstream interface, failure mode, and fallback/degradation behavior.
- **Quality Attributes & Trade-Offs**: Explicit analysis of how latency, consistency, durability, security, cost, and operability trade against one another.
- **Architecture Risks & Technical Debt**: Severity, affected components, concrete mitigation or remediation owner, and tracking link.
