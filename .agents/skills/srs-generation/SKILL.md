---
name: srs-generation
description: Synthesizes models/requirements/ into docs/product/02-requirements/SRS.md.
---

# Skill: IEEE-Compatible SRS Generation (`SKILL-004`)

## 1. Description

Synthesizes normalized requirements models (`models/requirements/`) into `docs/product/02-requirements/SRS.md`.

## 2. Trigger Conditions

- Phase `02-requirements` when generating or updating `SRS.md` (`requirements-engineer`).

## 3. Authoritative Inputs

- `models/requirements/requirements.yaml`, `business-rules.yaml`, `acceptance-criteria.yaml`, `docs/specifications/`, `docs/templates/requirements/SRS.template.md`.

## 4. Preconditions

1. `docs/product/02-requirements/README.md` read; `models/requirements/*.yaml` validated.

## 5. Execution Procedure

1. Read all canonical models in `models/requirements/` and shared specs in `docs/specifications/`.
2. Populate `docs/product/02-requirements/SRS.md` strictly from `docs/templates/requirements/SRS.template.md`.
3. Cross-reference every `FR-###`, `NFR-###`, `BR-###`, and `AC-###` to upstream capabilities and downstream use cases/tests.
4. Run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `docs/product/02-requirements/SRS.md` and `traceability-matrix.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Do not promote `SRS.md` to `APPROVED` if any requirement lacks acceptance criteria or has unresolved `[OPEN QUESTION]` tags.

## 9. Restrictions

- Never introduce requirements in `SRS.md` that do not exist in `models/requirements/`.

## 10. Related Skills

- `requirements-engineering`, `use-case-modeling`, `traceability-audit`
