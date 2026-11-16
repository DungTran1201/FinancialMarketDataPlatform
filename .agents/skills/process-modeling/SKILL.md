---
name: process-modeling
description: Models cross-actor workflows and BPMN/swimlane diagrams inside capability workflows/ directories.
---

# Skill: Business Process, BPMN & Swimlane Modeling (`SKILL-006`)

## 1. Description

Models multi-step operational and business workflows, actor handoffs, decision gateways, compensating branches, and derived BPMN/swimlane Mermaid diagrams inside `<capability>/workflows/` and `docs/overview/cross-plane-interactions.md`.

## 2. Trigger Conditions

- Lifecycle Stage 3 (`Specification`) or Stage 4 (`Architecture and Design`) for capabilities requiring `ART-WORKFLOW` / `ART-DIAG-BPMN` (`process-modeler`).

## 3. Authoritative Inputs

- `docs/governance/standards/diagram-standards.md`, `docs/governance/templates/product-and-requirements/workflow-specification.template.md`, `docs/governance/templates/diagrams/bpmn-diagram.template.md`, owning `capability.yaml`, and `requirements/`.

## 4. Preconditions

1. Owning `capability.yaml` and upstream `FR`/`RULE`/`UC` specifications read; triggering events and actors verified.

## 5. Execution Procedure

1. Author or update `<capability>/workflows/workflow-specification.md` (or capability workflow spec) from `workflow-specification.template.md`.
2. Derive BPMN/swimlane Mermaid diagrams inside `<capability>/workflows/` from `bpmn-diagram.template.md` with `source_of_truth.is_authoritative: false` and `Diagram Metadata` + `Legend` sections.
3. Update `quality/traceability.yaml` and `capability.yaml` `required_artifacts`, then run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- `<capability>/workflows/*.md` workflow specifications and derived BPMN/swimlane Mermaid views.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python tools/validators/run_all.py
```

## 8. Failure Handling

- Tag unverified workflow handoffs or retry/SLA boundaries as `[OPEN]`; fix all validator errors before finishing.

## 9. Restrictions

- Never treat a workflow diagram as standalone truth without an upstream workflow or requirement specification; never create `docs/diagrams/process/`.

## 10. Related Skills

- `use-case-modeling`, `diagram-modeling`, `traceability-audit`
