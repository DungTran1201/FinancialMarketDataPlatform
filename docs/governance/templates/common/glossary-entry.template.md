---
doc_id: TPL-COM-GLOSS-001
title: "Template: Ubiquitous Language Glossary Entry"
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
    - "docs/governance/templates/common/glossary-entry.template.md"
related_docs:
  - GOV-TPL-ROOT-001
  - GOV-STD-WRIT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created ubiquitous language glossary entry template."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial V2 glossary entry template."
---

# Template: Ubiquitous Language Glossary Entry

Use this template in `overview/glossary.md` or `<domain>/domain-specification.md` to eliminate conflicting definitions across business, data, API, and AI planes.

---

# Glossary: `<Domain or Platform>`

## Term Definitions `[REQUIRED]`

| Term | Canonical Definition | Bounded Context / Plane | Prohibited Synonyms / Ambiguities | Code / Schema Symbol |
|---|---|---|---|---|
| `<Canonical Term>` | `<Unambiguous technical and business definition>` | `<plane / domain>` | `<Terms not to confuse with this concept>` | `<ClassOrTableOrField>` |

## Calculation & Unit Semantics `[CONDITIONAL: Required for quantitative or financial terms]`

| Term | Formula / Invariant | Precision / Type | Time Semantics |
|---|---|---|---|
| `<Metric>` | `<Exact mathematical formula>` | `<e.g., Decimal(38,18)>` | `<e.g., UTC event_time vs ingested_at>` |
