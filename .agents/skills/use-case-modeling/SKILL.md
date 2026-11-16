---
name: use-case-modeling
description: Models actor-goal use cases (UC-*) inside capability use-cases/ directories in Documentation V2.
---

# Skill: Use Case Catalog & Specification Modeling (`SKILL-007`)

## 1. Description

Models actor goals, triggers, preconditions, main/alternative/exception flows, and postconditions (`UC-<DOM>-NNN`) inside `<capability>/use-cases/`.

## 2. Trigger Conditions

- Lifecycle Stage 3 (`Specification`) or `HIGH_CRITICAL` capabilities requiring `ART-USE-CASE` per `artifact-applicability-matrix.yaml` (`requirements-engineer`, `business-analyst`).

## 3. Authoritative Inputs

- `docs/governance/standards/requirements-standards.md`, `docs/governance/templates/product-and-requirements/use-case.template.md`, owning `capability.yaml`, and `<capability>/requirements/capability-specification.md`.

## 4. Preconditions

1. Owning `capability.yaml` read and upstream requirements (`FR-*`, `RULE-*`) defined.

## 5. Execution Procedure

1. Author `<capability>/use-cases/uc-*.md` specifications from `use-case.template.md`, linking to owning `FR-*` and `RULE-*` IDs.
2. Ensure actor personas match verified roles (`UserRole` in `src/serving/api/modules/iam/domain/ports.py` or Data Plane components).
3. Link use cases in `quality/traceability.yaml` (`rule_or_use_case_ids`) and run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- `<capability>/use-cases/*.md` specifications and updated `quality/traceability.yaml`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python tools/validators/run_all.py
```

## 8. Failure Handling

- Tag unconfirmed actor permissions or exception flows as `[OPEN]`; fix all validator errors.

## 9. Restrictions

- Never invent actors or use cases not traced to verified code or capability requirements; never create V1 `docs/product/04-use-cases/`.

## 10. Related Skills

- `requirements-engineering`, `process-modeling`, `test-modeling`
