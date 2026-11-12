# Product & Frontend Architecture Decision Records (`docs/product/06-architecture/adr/`)

## 1. Directory Purpose

Stores product-specific and frontend-specific Architecture Decision Records (`WEB-ADR-###`) that complement the core platform ADRs in `docs/architecture/adr/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: `WEB-ADR-<NNN>-<slug>.md` files governing product/frontend architectural trade-offs.
- **Does NOT belong in this directory**: Core Data Platform, Backend, Storage, Caching, or Agent Plane ADRs (which live in `docs/architecture/adr/ADR-001..006`).

## 3. Agent Role and Responsibilities

Authored by `architecture-modeler` and `ux-modeler`; audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/architecture/adr/README.md` — Shared platform ADRs (`ADR-001..006`).
2. `docs/templates/architecture/ADR.template.md` — Standard ADR template.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `WEB-ADR-<NNN>-<slug>.md` | Product/Website Architecture Decision Record | Conditional | `docs/templates/architecture/ADR.template.md` |

## 6. Directory and File Organization

Flat directory `docs/product/06-architecture/adr/` with files named `WEB-ADR-<NNN>-<kebab-slug>.md`.

## 7. Document Creation Rules

Use `WEB-ADR-###` prefix to prevent ID collisions with `ADR-001..006` in `docs/architecture/adr/`.

## 8. Creation Workflow

1. Read `docs/product/06-architecture/adr/README.md` and `docs/architecture/adr/README.md`.
2. Verify the decision is not already governed by `ADR-001..006`.
3. Instantiate `docs/templates/architecture/ADR.template.md` with ID `WEB-ADR-<NNN>`.
4. Register the decision in `models/architecture/architecture.yaml`.
5. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Complements `docs/architecture/adr/` for Website/Product layer decisions.

## 10. Quality Gate

All `WEB-ADR-###` files follow `ADR.template.md` and do not contradict `ADR-001..006`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT duplicate or override `ADR-001` through `ADR-006` here.
- Do NOT use bare `ADR-001` IDs that collide with `docs/architecture/adr/`.
