# Domain Modeling Templates (`docs/templates/domain/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `07-domain`, targeting `docs/product/07-domain/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `domain` documentation (`domain-model.template.md, entity.template.md, aggregate.template.md, domain-rules.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/07-domain/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `domain-modeler`; review role: `architecture-modeler`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/07-domain/README.md` — Target lifecycle phase operating contract.
3. `models/domain/domain.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `domain-model.template.md` | DDD Domain Model & Bounded Context Specification (`DOM-MOD-[NNN]`) | Required | `docs/templates/domain/domain-model.template.md` |
| `entity.template.md` | Domain Entity & Value Object Catalog (`DOM-ENT-[NNN]`) | Required | `docs/templates/domain/entity.template.md` |
| `aggregate.template.md` | DDD Aggregate Root & Transactional Boundary Specification (`DOM-AGG-[NNN]`) | Required | `docs/templates/domain/aggregate.template.md` |
| `domain-rules.template.md` | Domain Invariants & Validation Rules (`DOM-RULE-[NNN]`) | Required | `docs/templates/domain/domain-rules.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/domain/` containing `README.md` and 4 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/domain/README.md` and `docs/product/07-domain/README.md`.
2. Inspect authoritative canonical model `models/domain/domain.yaml`.
3. Copy the selected `.template.md` file to `docs/product/07-domain/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/07-domain/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/domain/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
