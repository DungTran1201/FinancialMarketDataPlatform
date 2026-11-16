---
doc_id: TPL-REQ-BRIEF-001
title: "Template: Product Brief"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: business-analyst
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/product-and-requirements/product-brief.template.md"
related_docs:
  - GOV-STD-REQ-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Product Brief template with required/conditional markers and open-question discipline."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial V2 Product Brief template."
---

# Template: Product Brief

Defines high-level business intent, target users, and explicit scope boundaries (`in-scope` vs `out-of-scope`) before decomposing into Domain and Capability specifications.

---

# Product Brief: `<Product / Initiative Name>`

## 1. Problem Statement & Business Objectives `[REQUIRED]`

- **Problem**: `<Measurable pain point or gap>`
- **Objectives (`BR-...`)**:
  - `BR-<DOM>-001`: `<Concrete business outcome and measurable value>`

## 2. Target Actors & Stakeholders `[REQUIRED]`

| Actor / Role | Goal | Plane Touchpoints |
|---|---|---|
| `<Actor>` | `<Primary job-to-be-done>` | `<application-plane / data-plane / intelligence-plane>` |

## 3. Scope Boundaries `[REQUIRED]`

### In Scope
- `<Explicitly included capability or workflow>`

### Out of Scope
- `<Explicitly excluded capability or deferred milestone>`

## 4. Assumptions, Dependencies & Open Questions `[REQUIRED]`

| ID | Type (`ASSUMPTION | OPEN`) | Statement | Owner | Resolution Target / Impact |
|---|---|---|---|---|
| `OQ-001` | `OPEN` | `<Unresolved business or product decision>` | `<Owner>` | `<Impact if unresolved>` |
