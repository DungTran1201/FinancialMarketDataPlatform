---
doc_id: TPL-ARCH-DESC-001
title: "Template: Architecture Description (arc42-Adapted)"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: system-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/architecture/architecture-description.template.md"
related_docs:
  - GOV-STD-ARCH-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created arc42-adapted scoped architecture description template."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Initial V2 architecture description template."
---

# Template: Architecture Description (arc42-Adapted)

Use for **Platform Overview** (`overview/`) or **Plane Architecture** (`<plane>/architecture/`). Keep strictly scoped to the owning boundary.

---

# Architecture Description: `<Platform Overview or Plane Name>`

## 1. Scope, Quality Goals & Constraints `[REQUIRED]`

- **Architectural Scope**: `<Boundaries of this plane or system context>`
- **Top Quality Attributes**: `<Ranked attributes linked to NFRs>`
- **Constraints**: `<Hard technology, security, or dependency rules>`

## 2. Context & External Boundaries `[REQUIRED]`

- Reference C4 Context / Container Diagram (`DIAG-...`) and summarize upstream/downstream contracts.

## 3. Building Block & Dependency Structure `[REQUIRED]`

| Building Block / Domain | Responsibility | Allowed Dependencies | Forbidden Dependencies |
|---|---|---|---|
| `<Block>` | `<Owned responsibility>` | `<Upstream blocks>` | `<Prohibited cross-plane calls>` |

## 4. Runtime & Cross-Cutting Concepts `[CONDITIONAL: Required for Plane architectures]`

- **Data Flow & Delivery**: `<Sync vs async, backpressure, idempotency>`
- **Security & Isolation**: `<Auth, trust zones, DB least privilege>`
- **Observability & Resilience**: `<Metrics, tracing, graceful degradation>`

## 5. Current Implementation (`AS-IS`) vs. Target Architecture (`TARGET`) `[REQUIRED]`

| Component / Mechanism | AS-IS Reality (Code Evidence) | TARGET Design | Migration / Remediation Gap |
|---|---|---|---|
| `<Component>` | `<IMPLEMENTED / SIMULATED / NOT_IMPLEMENTED + paths>` | `<Target container/protocol>` | `<Explicit gap or blocker>` |

## 6. Architecture Decisions, Risks & Trade-Offs `[REQUIRED]`

- **Linked ADRs**: `<Links to MADR decisions>`
- **Risks & Trade-Offs**: `<Explicit risk rating, trade-off rationale, mitigation>`
