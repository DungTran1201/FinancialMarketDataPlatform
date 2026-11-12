# API & Integration Contract Templates (`docs/templates/api/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `08-api`, targeting `docs/product/08-api/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `api` documentation (`API-specification.template.md, API-contract.template.md, integration-contract.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/08-api/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `api-architect`; review role: `security-reviewer`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/08-api/README.md` — Target lifecycle phase operating contract.
3. `models/api/api.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `API-specification.template.md` | API Domain Specification (`API-SPEC-[NNN]`) | Required | `docs/templates/api/API-specification.template.md` |
| `API-contract.template.md` | Detailed Endpoint API Contract (`API-CTR-[NNN]`) | Required | `docs/templates/api/API-contract.template.md` |
| `integration-contract.template.md` | External & Inter-Plane Integration Contract (`API-INT-[NNN]`) | Required | `docs/templates/api/integration-contract.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/api/` containing `README.md` and 3 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/api/README.md` and `docs/product/08-api/README.md`.
2. Inspect authoritative canonical model `models/api/api.yaml`.
3. Copy the selected `.template.md` file to `docs/product/08-api/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/08-api/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/api/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
