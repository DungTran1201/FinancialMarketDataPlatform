---
doc_id: GOV-TPL-ROOT-001
title: "Documentation V2 Governance Templates Index"
doc_type: index
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: documentation-tooling-engineer
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/README.md"
related_docs:
  - GOV-CAT-ART-001
  - GOV-CAT-MAT-001
  - GOV-STD-WRIT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Indexed all Documentation V2 governance templates organized by engineering discipline and diagram type."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-tooling-engineer
    summary: "Initial Documentation V2 templates index."
---

# Governance Templates Library

Templates provide repeatable structures for Phase 2 documentation. **Do NOT instantiate templates blindly or leave empty placeholder files.** Check [artifact-applicability-matrix.yaml](../catalog/artifact-applicability-matrix.yaml) for which artifacts are `REQUIRED`, `CONDITIONAL`, `RECOMMENDED`, or `NOT_APPLICABLE_WITH_REASON` based on capability risk tier and technical signals.

Every Markdown template distinguishes `[REQUIRED]`, `[CONDITIONAL]`, and `[OPTIONAL]` sections.

## Categories

- `common/`: `document-frontmatter.template.yaml`, `readme.template.md`, `glossary-entry.template.md`
- `product-and-requirements/`: `product-brief.template.md`, `system-requirements.template.md`, `domain-specification.template.md`, `capability-specification.template.md`, `capability.template.yaml`, `use-case.template.md`, `business-rules.template.md`, `workflow-specification.template.md`, `nfr.template.md`
- `architecture/`: `architecture-description.template.md`, `component-design.template.md`, `adr.template.md`, `agent-specification.template.md`
- `interfaces-and-data/`: `openapi.template.yaml`, `asyncapi.template.yaml`, `error-catalog.template.md`, `data-contract.template.yaml`, `data-model.template.md`, `database-design.template.md`
- `security/`: `threat-model.template.md`, `security-requirements.template.md`, `authorization-matrix.template.yaml`
- `quality/`: `test-plan.template.md`, `test-scenarios.template.md`, `test-cases.template.yaml`, `traceability.template.yaml`
- `operations/`: `deployment-description.template.md`, `runbook.template.md`, `observability-and-slo.template.md`, `incident-and-recovery.template.md`
- `diagrams/`: `c4-diagram.template.md`, `bpmn-diagram.template.md`, `sequence-diagram.template.md`, `state-machine-diagram.template.md`, `erd-diagram.template.md`, `data-flow-diagram.template.md`, `deployment-diagram.template.md`, `threat-model-diagram.template.md`, `agent-workflow-diagram.template.md`
