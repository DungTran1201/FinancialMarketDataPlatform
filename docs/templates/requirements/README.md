# Requirements Engineering Templates (`docs/templates/requirements/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `02-requirements`, targeting `docs/product/02-requirements/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `requirements` documentation (`SRS.template.md, functional-requirements.template.md, non-functional-requirements.template.md, business-rules.template.md, acceptance-criteria.template.md, traceability-matrix.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/02-requirements/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `requirements-engineer`; review role: `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/02-requirements/README.md` — Target lifecycle phase operating contract.
3. `models/requirements/requirements.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `SRS.template.md` | Software Requirements Specification (IEEE-Compatible SRS) (`REQ-SRS-[NNN]`) | Required | `docs/templates/requirements/SRS.template.md` |
| `functional-requirements.template.md` | Functional Requirements Specification (`REQ-FR-[NNN]`) | Required | `docs/templates/requirements/functional-requirements.template.md` |
| `non-functional-requirements.template.md` | Non-Functional Requirements (NFR) Specification (`REQ-NFR-[NNN]`) | Required | `docs/templates/requirements/non-functional-requirements.template.md` |
| `business-rules.template.md` | Business Rules & Domain Invariants Catalog (`REQ-BR-[NNN]`) | Required | `docs/templates/requirements/business-rules.template.md` |
| `acceptance-criteria.template.md` | Acceptance Criteria Catalog (`REQ-AC-[NNN]`) | Required | `docs/templates/requirements/acceptance-criteria.template.md` |
| `traceability-matrix.template.md` | Requirements Traceability Matrix (RTM) (`REQ-RTM-[NNN]`) | Required | `docs/templates/requirements/traceability-matrix.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/requirements/` containing `README.md` and 6 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/requirements/README.md` and `docs/product/02-requirements/README.md`.
2. Inspect authoritative canonical model `models/requirements/requirements.yaml`.
3. Copy the selected `.template.md` file to `docs/product/02-requirements/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/02-requirements/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/requirements/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
