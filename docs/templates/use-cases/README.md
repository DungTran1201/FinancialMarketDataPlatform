# Use Case Templates (`docs/templates/use-cases/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `04-use-cases`, targeting `docs/product/04-use-cases/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `use-cases` documentation (`use-case-model.template.md, use-case-catalog.template.md, use-case-specification.template.md, use-case-matrix.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/04-use-cases/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `requirements-engineer`; review role: `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/04-use-cases/README.md` — Target lifecycle phase operating contract.
3. `models/interaction/interactions.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `use-case-model.template.md` | Use Case Model & Actor Taxonomy (`UC-MOD-[NNN]`) | Required | `docs/templates/use-cases/use-case-model.template.md` |
| `use-case-catalog.template.md` | Use Case Catalog (`UC-CAT-[NNN]`) | Required | `docs/templates/use-cases/use-case-catalog.template.md` |
| `use-case-specification.template.md` | Detailed Use Case Specification (`UC-SPEC-[NNN]`) | Required | `docs/templates/use-cases/use-case-specification.template.md` |
| `use-case-matrix.template.md` | Use Case to Requirement & API Matrix (`UC-MAT-[NNN]`) | Required | `docs/templates/use-cases/use-case-matrix.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/use-cases/` containing `README.md` and 4 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/use-cases/README.md` and `docs/product/04-use-cases/README.md`.
2. Inspect authoritative canonical model `models/interaction/interactions.yaml`.
3. Copy the selected `.template.md` file to `docs/product/04-use-cases/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/04-use-cases/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/use-cases/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
