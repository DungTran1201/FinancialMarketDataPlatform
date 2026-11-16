---
doc_id: TPL-DIAG-C4-001
title: "Template: C4 Architecture Diagram (Context / Container / Component)"
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
    - "docs/governance/templates/diagrams/c4-diagram.template.md"
related_docs:
  - GOV-STD-DIAG-001
  - GOV-STD-ARCH-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created C4 diagram template covering Context (L1), Container (L2), and Component (L3) viewpoints."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Initial V2 C4 diagram template."
---

# Template: C4 Architecture Diagram

Use for **C4 Level 1 (System Context)**, **Level 2 (Container)**, or **Level 3 (Component)** views derived from an authoritative Architecture Description or Component Design document. When instantiated, set `doc_type: diagram`, `source_of_truth.is_authoritative: false`, and link the exact authoritative source document.

---

# Diagram: `<C4 Level> — <Scope Name>`

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-<SCOPE>-NNN` |
| **Title & Purpose** | `<Title — One-sentence analytical scope>` |
| **C4 Level** | `<Level 1 Context | Level 2 Container | Level 3 Component>` |
| **Owner Role & Scope** | `<owner-role> / <platform|plane|capability>` |
| **Authoritative Source** | `[<Source Doc Title>](<relative/path/to/source.md>)` (`<DOC-ID>`) |
| **Notation** | `Mermaid flowchart TB` (`C4 Model`) |
| **Version & Status** | `<X.Y.Z> — <DRAFT|IN_REVIEW|APPROVED|DEPRECATED>` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    actor_user["<User / Consumer Role> (External Actor)"]
    ext_sys["<External System Name> (Upstream Provider)"]

    subgraph boundary_scope["<System or Plane Boundary (C4 Scope)>"]
        comp_entry["<Entry Container / Component> (<Protocol / Runtime>)"]
        comp_core["<Core Processing Unit> (<Responsibility>)"]
        store_primary[("<Primary Store> (<Engine>)")]
    end

    actor_user -->|"HTTPS / Action"| comp_entry
    ext_sys -.->|"Async Feed / Event"| comp_entry
    comp_entry -->|"Command / Query"| comp_core
    comp_core -->|"Read / Write"| store_primary
```

## 3. Legend `[REQUIRED]`

- **Solid Arrow (`-->`)**: Synchronous request/response or blocking call (protocol labeled).
- **Dashed Arrow (`-.->`)**: Asynchronous message, stream, or scheduled batch transfer.
- **Dashed Subgraph Box**: Architectural system, plane, or container boundary.
- **Database Cylinder (`[(...)]`)**: Persistent state store or analytical storage tier.

## 4. Mapping Notes `[CONDITIONAL: Required when AS-IS differs from TARGET]`

- Explicitly note any depicted component or edge whose `implementation_status` is `SIMULATED` or `PLANNED` (MUST match Section 5 of the authoritative Architecture Description).
