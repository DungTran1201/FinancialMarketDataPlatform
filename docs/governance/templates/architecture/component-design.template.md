---
doc_id: TPL-ARCH-COMP-001
title: "Template: Component Design Specification"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/architecture/component-design.template.md"
related_docs:
  - GOV-STD-ARCH-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Component Design template for capability-level module boundaries, ports/adapters, and error handling."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Initial V2 component design template."
---

# Template: Component Design Specification

Instantiated inside `<capability>/design/` for backend services, frontend SPA modules, streaming workers, or lakehouse engines.

---

# Component Design: `<Component Name>` (`<COMP-DOM-NNN>`)

## 1. Responsibility & Requirement Mapping `[REQUIRED]`

- **Mapped Requirements**: `FR-...`, `NFR-...`, `RULE-...`
- **Source Code Root**: `<src/... or frontend/src/...>`
- **Diagram Reference**: `<Optional C4 Level 3 / Sequence / State diagram>`

## 2. Internal Layers, Interfaces & Dependencies `[REQUIRED]`

| Layer / Module | Symbols (`Classes / Functions / Ports`) | Dependency Rule |
|---|---|---|
| `<domain / application / infrastructure / presentation>` | `<Exact symbols>` | `<Allowed imports>` |

## 3. Integration, Concurrency & Error Handling `[REQUIRED]`

- **External Adapters / Ports**: `<Cache, OLAP, HTTP client, broker ports>`
- **Concurrency & Rate/Resource Bounds**: `<Async locks, timeouts, batch sizes, query limits>`
- **Failure & Fallback Behavior**: `<Exact exception handling, fallback paths, DLQ routing>`

## 4. `AS-IS` vs. `TARGET` Implementation Notes `[REQUIRED]`

- `<Explicit statement of what is live vs. in-memory/simulated/stubbed>`
