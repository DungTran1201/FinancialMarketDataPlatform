---
name: requirements-engineering
description: Models FR, NFR, BR, and AC in models/requirements/ and docs/product/02-requirements/.
---

# Skill: Requirements Engineering & Normalization (`SKILL-003`)

## 1. Description

Extracts, normalizes, and models capabilities (`CAP-###`), functional (`FR-###`), non-functional (`NFR-###`), business rules (`BR-###`), and acceptance criteria (`AC-###`).

## 2. Trigger Conditions

- Phase `02-requirements` or requirement/business-rule changes (`requirements-engineer`).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/product/02-requirements/README.md`, `docs/specifications/data-requirements.md`, `non-functional-requirements.md`, `models/requirements/`, `docs/templates/requirements/`.

## 4. Preconditions

1. Target `README.md` read; preserved IDs (`FR-01..10`) verified in `.agents/config/identifier-registry.yaml`.

## 5. Execution Procedure

1. Inspect `models/requirements/*.yaml` (`requirements.yaml`, `business-rules.yaml`, `acceptance-criteria.yaml`, `glossary.yaml`) and baseline `docs/specifications/`.
2. Update `models/requirements/*.yaml` first with atomic, testable statements and `CAP -> FR/NFR/BR -> AC` links.
3. Synchronize `docs/product/02-requirements/` using `docs/templates/requirements/`.
4. Tag unconfirmed requirements with `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`.
5. Run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `models/requirements/*.yaml` and `docs/product/02-requirements/*.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Record missing acceptance thresholds as `[OPEN QUESTION]`, keep status `DRAFT`, and resolve all validator errors.

## 9. Restrictions

- Never renumber or delete preserved IDs (`FR-01..10`); never invent unverified business rules.

## 10. Related Skills

- `srs-generation`, `use-case-modeling`, `traceability-audit`
