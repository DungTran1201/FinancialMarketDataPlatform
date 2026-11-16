---
doc_id: TPL-REQ-RULE-001
title: "Template: Business Rules Specification"
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
    - "docs/governance/templates/product-and-requirements/business-rules.template.md"
related_docs:
  - GOV-STD-REQ-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Business Rules template capturing invariants, formulas, enforcement boundaries, and violation consequences."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial V2 Business Rules template."
---

# Template: Business Rules Specification

Captures domain invariants, calculation policies, and constraints that govern behavior independently of UI or storage implementation.

---

# Business Rules: `<Domain or Capability Name>`

## 1. Rule Catalog `[REQUIRED]`

| Rule ID | Rule Name | Rule Expression / Invariant | Applies To (`FR`/`UC`/`Entity`) | Enforcement Boundary | Violation Handling |
|---|---|---|---|---|---|
| `RULE-<DOM>-001` | `<Short Name>` | `<Exact unambiguous condition or formula>` | `FR-<DOM>-001` | `<Validation / Domain / Sink>` | `<Reject HTTP 422 / Route to DLQ / Block promotion>` |

## 2. Edge Cases & Precision / Time Semantics `[CONDITIONAL: Required for numeric, temporal, or financial rules]`

- **Numeric Type & Rounding**: `<Exact scale/precision and rounding mode>`
- **Timezone & Ordering**: `<UTC rule and out-of-order / late-arrival tie-breaker>`

## 3. Verification Mapping `[REQUIRED]`

- `<Links to deterministic TC-... test cases>`
