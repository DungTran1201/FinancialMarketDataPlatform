---
name: domain-modeling
description: Models Domain boundaries, glossaries, logical data models, DB designs, and ERDs in Documentation V2.
---

# Skill: DDD Domain, Entity & Data Modeling (`SKILL-008`)

## 1. Description

Models Domain bounded contexts (`domain-specification.md`), ubiquitous terminology (`glossary.md`), conceptual/logical data models (`data/data-model.md`), physical DB designs (`data/database-design.md`), and Crow's Foot ERDs (`data/*-erd.md`) across OLTP, Hot State, OLAP, and Lakehouse stores.

## 2. Trigger Conditions

- Lifecycle Stage 3/4 (`Specification` / `Design`), `domain-modeling`, or `schema-migration` changes (`domain-modeler`, `database-architect`).

## 3. Authoritative Inputs

- `docs/governance/standards/data-and-database-standards.md`, `docs/governance/templates/interfaces-and-data/{data-model,database-design}.template.md`, `docs/governance/templates/product-and-requirements/domain-specification.template.md`, `deploy/postgres/init/01_schema.sql`, `deploy/clickhouse/init/01_schema.sql`, `deploy/iceberg/catalog-config.yaml`, `src/shared/domain/`, and `src/**/domain/`.

## 4. Preconditions

1. Owning Domain `README.md` / `capability.yaml` read; `Decimal` precision and UTC timestamp invariants (`DATA-RULE-002`) verified.

## 5. Execution Procedure

1. Maintain `<plane>/domains/<domain>/domain-specification.md` and `glossary.md` for domain-wide entities and ubiquitous terms.
2. Author `<capability>/data/data-model.md` (engine-independent entities, natural keys, precision) and `<capability>/data/database-design.md` (physical DDL, indexes, partitions, migrations, rollback).
3. Enforce exact `Decimal` monetary/quantity types, UTC timestamps, and pure domain isolation in `src/**/domain/`.
4. Synchronize derived Mermaid ERDs (`data/*-erd.md`) using `docs/governance/templates/diagrams/erd-diagram.template.md` and run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- `<domain>/{domain-specification,glossary}.md` and `<capability>/data/{data-model.md,database-design.md,*-erd.md}`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/architecture/ -v
```

## 8. Failure Handling

- Tag unresolved schema conflicts (e.g., DDL vs Iceberg config primary key mismatches) as `[OPEN]` in `capability.yaml`; fix all validator errors.

## 9. Restrictions

- Never use `float` for persisted financial values; never introduce ORM/HTTP/driver imports into `domain/` packages; never recreate V1 `models/domain/`.

## 10. Related Skills

- `api-contract`, `analytics-engineering-dbt-clickhouse`, `data-governance-lineage`
