---
doc_id: "DOC-GOV-ROOT"
title: "Documentation Governance & Standards"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "NOT_APPLICABLE"
owner: "System Analyst & Principal Software Architect"
purpose: "Defines documentation metadata requirements, lifecycle statuses, validator rationale, and phase gate review rules."
scope: "All documentation, specifications, diagrams, and work items in docs/."
dependencies:
  - "AGENTS.md"
  - "docs/README.md"
references:
  - "docs/governance/standards.md"
  - ".agents/README.md"
assumptions:
  - "Agents obey documentation-first gates prior to coding."
open_issues: []
review_criteria:
  - "Explicitly documents replacement of legacy V2 validator per DEC-P0-001"
  - "Passes tools/validators/run_all.py"
---

# Documentation Governance (`docs/governance/`)

This directory houses standards, templates, lifecycle checklists, and governance decisions for greenfield documentation.

## Contents & Naming Conventions
- Use `kebab-case.md` filenames.
- Authoritative governance spec: [standards.md](standards.md).

## Dependencies & Agent Rules
- Depends on root [AGENTS.md](../../AGENTS.md) and [.agents/hooks.json](../../.agents/hooks.json).
- Every file created here is checked automatically by [validate_greenfield.py](../../tools/validators/validate_greenfield.py).
