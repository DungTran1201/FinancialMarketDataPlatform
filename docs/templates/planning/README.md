# Planning Templates (`docs/templates/planning/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `01-planning`, targeting `docs/product/01-planning/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `planning` documentation (`project-plan.template.md, WBS.template.md, implementation-roadmap.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/01-planning/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `documentation-architect`; review role: `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/01-planning/README.md` — Target lifecycle phase operating contract.
3. `models/requirements/requirements.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `project-plan.template.md` | Project Engineering & Delivery Plan (`PLAN-PRJ-[NNN]`) | Required | `docs/templates/planning/project-plan.template.md` |
| `WBS.template.md` | Work Breakdown Structure (WBS) (`PLAN-WBS-[NNN]`) | Required | `docs/templates/planning/WBS.template.md` |
| `implementation-roadmap.template.md` | Phased Implementation Roadmap (`PLAN-RDMP-[NNN]`) | Required | `docs/templates/planning/implementation-roadmap.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/planning/` containing `README.md` and 3 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/planning/README.md` and `docs/product/01-planning/README.md`.
2. Inspect authoritative canonical model `models/requirements/requirements.yaml`.
3. Copy the selected `.template.md` file to `docs/product/01-planning/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/01-planning/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/planning/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
