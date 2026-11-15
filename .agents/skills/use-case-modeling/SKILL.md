---
name: use-case-modeling
description: Actor goals, flows, and UC-### specs in docs/product/04-use-cases/.
---

# Skill: Use Case Catalog & Specification Modeling (`SKILL-007`)

## 1. Description

Models actor goals, preconditions, main/alternative/exception flows, and postconditions (`UC-###`) in `docs/product/04-use-cases/`.

## 2. Trigger Conditions

- Phase `04-use-cases` or user/system interaction scope changes (`requirements-engineer`).

## 3. Authoritative Inputs

- `models/requirements/requirements.yaml`, `models/context/` (or `models/architecture/architecture.yaml`) and `models/requirements/requirements.yaml`, `docs/product/04-use-cases/README.md`, `docs/templates/use-cases/`.

## 4. Preconditions

1. Target `README.md` read; actors (`ACT-###`) and upstream requirements (`FR-###`) defined in `models/`.

## 5. Execution Procedure

1. Register or update `UC-###` entries in `models/requirements/requirements.yaml` and `docs/product/04-use-cases/use-case-catalog.md`.
2. Author detailed specifications in `docs/product/04-use-cases/specifications/` using `docs/templates/use-cases/`.
3. Synchronize derived use-case diagrams in `docs/diagrams/use-case/`.
4. Run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `docs/product/04-use-cases/use-case-catalog.md`, `specifications/UC-###-*.md`, `docs/diagrams/use-case/*.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Tag unconfirmed actor permissions or exception flows as `[OPEN QUESTION]`; fix all validator errors.

## 9. Restrictions

- Never invent actors or use cases not traced to an approved or proposed `FR-###` / `CAP-###`.

## 10. Related Skills

- `requirements-engineering`, `process-modeling`, `test-modeling`
