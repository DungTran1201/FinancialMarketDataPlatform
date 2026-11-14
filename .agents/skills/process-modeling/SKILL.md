---
name: process-modeling
description: BPMN and swimlane workflows in models/process/ and docs/product/03-business-process/.
---

# Skill: Business Process, BPMN & Swimlane Modeling (`SKILL-006`)

## 1. Description

Models operational and business workflows (`PROC-###`), BPMN flows (`DIAG-BPMN-*`), and actor swimlanes (`DIAG-SWIM-*`).

## 2. Trigger Conditions

- Phase `03-business-process` or operational workflow changes (`process-modeler`).

## 3. Authoritative Inputs

- `models/process/processes.yaml`, `models/requirements/`, `docs/product/03-business-process/README.md`, `docs/templates/business-process/`.

## 4. Preconditions

1. Target `README.md` read; triggering events, actors, and upstream `FR-###`/`BR-###` identified.

## 5. Execution Procedure

1. Update `models/process/processes.yaml` first with `PROC-###` IDs, actors, steps, happy/exception paths, and requirement links.
2. Author process specifications in `docs/product/03-business-process/` from `docs/templates/business-process/`.
3. Synchronize derived Mermaid diagrams in `docs/diagrams/process/bpmn/` and `docs/diagrams/process/swimlane/`.
4. Run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `models/process/processes.yaml`, `docs/product/03-business-process/*.md`, `docs/diagrams/process/**/*.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Tag unverified workflow handoffs as `[OPEN QUESTION]`; fix all validator errors before finishing.

## 9. Restrictions

- Never use a process diagram as a standalone source of truth without updating `models/process/processes.yaml`.

## 10. Related Skills

- `use-case-modeling`, `diagram-modeling`, `traceability-audit`
