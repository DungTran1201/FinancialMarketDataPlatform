---
name: domain-modeling
description: DDD bounded contexts, aggregates, entities, and invariants in models/domain/.
---

# Skill: DDD Domain, Entity & Aggregate Modeling (`SKILL-008`)

## 1. Description

Models DDD bounded contexts (`DOM-###`), aggregates, entities (`ENT-###`), value objects, and financial domain invariants in `models/domain/` and `docs/product/07-domain/`.

## 2. Trigger Conditions

- Phase `07-domain` or domain entity/schema/dictionary changes (`domain-modeler`).

## 3. Authoritative Inputs

- `models/domain/domain.yaml`, `entities.yaml`, `data-dictionary.yaml`, `docs/specifications/data-dictionary.md`, `src/backend/modules/*/domain/`, `docs/templates/domain/`.

## 4. Preconditions

1. Target `README.md` read; `Decimal` precision and UTC timestamp invariants (`DATA-RULE-002`) verified.

## 5. Execution Procedure

1. Update `models/domain/domain.yaml`, `entities.yaml`, and `data-dictionary.yaml` first with `DOM-###` and `ENT-###` IDs.
2. Enforce exact `Decimal` monetary/quantity types, UTC timestamps, and zero framework dependencies in `src/backend/modules/*/domain/`.
3. Synchronize `docs/product/07-domain/` and `docs/specifications/data-dictionary.md` using `docs/templates/domain/`.
4. Update derived class/ER diagrams in `docs/diagrams/domain/` and run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `models/domain/*.yaml`, `docs/product/07-domain/*.md`, `docs/diagrams/domain/*.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Tag unresolved entity ownership or grain ambiguities as `[OPEN QUESTION]`; fix all validator errors.

## 9. Restrictions

- Never use `float` for financial values; never introduce ORM/HTTP/driver imports into `domain/` packages.

## 10. Related Skills

- `api-contract`, `analytics-engineering-dbt-clickhouse`, `data-governance-lineage`
