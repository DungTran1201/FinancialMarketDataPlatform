---
doc_id: "DOC-WI-ROOT"
title: "Work Items & Traceability Lifecycle Index"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "NOT_APPLICABLE"
owner: "System Analyst & Engineering Leads"
purpose: "Tracks phase-scoped engineering work items across BACKLOG -> READY -> IN_PROGRESS -> BLOCKED -> IN_REVIEW -> TESTING -> ACCEPTED -> COMPLETE."
scope: "All Phases 0 through 9 on branch greenfield/main."
dependencies:
  - ".agents/workflows/phase-lifecycle.md"
  - "docs/product/requirements-traceability-matrix.md"
references:
  - "tools/validators/validate_greenfield.py"
assumptions:
  - "Work items validate structurally via YAML work_items frontmatter checks."
open_issues: []
review_criteria:
  - "Zero COMPLETE items without concrete test/measurement evidence"
---

# Work Items (`docs/work-items/`)

All engineering tasks across Phases 0–9 are tracked in machine-validated Work Item registers (`phase-<n>-work-items.md`).

## Required Fields (`Section 9`)
Every work item MUST define: `work_item_id`, `objective`, `scope`, `dependencies`, `prerequisites`, `steps`, `affected_modules`, `test_requirements`, `acceptance_criteria`, `risks`, `evidence`, and `status`.
