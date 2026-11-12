# Business Process Templates (`docs/templates/business-process/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `03-business-process`, targeting `docs/product/03-business-process/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `business-process` documentation (`process-model.template.md, BPMN.template.md, swimlane.template.md, process-catalog.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/03-business-process/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `process-modeler`; review role: `requirements-engineer`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/03-business-process/README.md` — Target lifecycle phase operating contract.
3. `models/process/processes.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `process-model.template.md` | Business Process Model Specification (`PROC-MOD-[NNN]`) | Required | `docs/templates/business-process/process-model.template.md` |
| `BPMN.template.md` | BPMN Process Specification (`PROC-BPMN-[NNN]`) | Required | `docs/templates/business-process/BPMN.template.md` |
| `swimlane.template.md` | Cross-Functional Swimlane Specification (`PROC-SWIM-[NNN]`) | Required | `docs/templates/business-process/swimlane.template.md` |
| `process-catalog.template.md` | Business Process Catalog (`PROC-CAT-[NNN]`) | Required | `docs/templates/business-process/process-catalog.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/business-process/` containing `README.md` and 4 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/business-process/README.md` and `docs/product/03-business-process/README.md`.
2. Inspect authoritative canonical model `models/process/processes.yaml`.
3. Copy the selected `.template.md` file to `docs/product/03-business-process/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/03-business-process/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/business-process/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
