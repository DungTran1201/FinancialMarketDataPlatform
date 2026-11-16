---
doc_id: TPL-ARCH-ADR-001
title: "Template: Architecture Decision Record (MADR 4.0.0)"
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
    - "docs/governance/templates/architecture/adr.template.md"
related_docs:
  - GOV-STD-ARCH-001
  - GOV-STD-REG-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created MADR 4.0.0-aligned Architecture Decision Record template."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Initial V2 MADR 4.0.0 ADR template."
---

# Template: Architecture Decision Record (MADR 4.0.0)

Place in `overview/decisions/`, `<plane>/decisions/`, or `<capability>/decisions/` matching the decision's blast radius. **Never set `status: APPROVED` unless explicitly ratified by the accountable architect.**

---

# `<ADR-SCOPE-NNN>: <Short Present-Tense Imperative Title>`

- **Status**: `DRAFT | IN_REVIEW | APPROVED | DEPRECATED`
- **Decision Date**: `YYYY-MM-DD` (or `PENDING` while `DRAFT`)
- **Deciders**: `<Accountable Architect / Owner Roles>`

## 1. Context and Problem Statement `[REQUIRED]`

`<Describe the architectural problem, constraints, and forces requiring a decision.>`

## 2. Decision Drivers `[REQUIRED]`

- `<Driver 1: e.g., latency, consistency, isolation, maintainability, cost>`
- `<Driver 2>`

## 3. Considered Options `[REQUIRED]`

1. `<Option 1>`
2. `<Option 2>`
3. `<Option 3>`

## 4. Decision Outcome `[REQUIRED]`

Chosen option: **"<Option N>"**, because `<concise justification tied to decision drivers>`.

### Consequences `[REQUIRED]`
- Good, because `<positive technical or operational effect>`
- Bad, because `<trade-off, added complexity, or constraint accepted>`

## 5. Pros and Cons of the Options `[OPTIONAL]`

### `<Option 1>`
- Good, because `<...>`
- Bad, because `<...>`

## 6. Confirmation & Traceability `[CONDITIONAL: Required when APPROVED]`

- **Verified By**: `<Test suite, architecture AST check, or benchmark>`
- **Superseded By**: `<ADR-... or None>`
