# UX & Frontend Specification Templates (`docs/templates/ux/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `11-ux`, targeting `docs/product/11-ux/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `ux` documentation (`information-architecture.template.md, screen-specification.template.md, user-flow.template.md, interaction-specification.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/11-ux/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `ux-modeler`; review role: `requirements-engineer`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/11-ux/README.md` — Target lifecycle phase operating contract.
3. `models/ux/ux.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `information-architecture.template.md` | Information Architecture & Navigation Specification (`UX-IA-[NNN]`) | Required | `docs/templates/ux/information-architecture.template.md` |
| `screen-specification.template.md` | UX Screen Specification (`UX-SCR-[NNN]`) | Required | `docs/templates/ux/screen-specification.template.md` |
| `user-flow.template.md` | User Flow & Journey Specification (`UX-FLOW-[NNN]`) | Required | `docs/templates/ux/user-flow.template.md` |
| `interaction-specification.template.md` | UI Micro-Interaction & Real-Time Streaming Behavior Specification (`UX-INT-[NNN]`) | Required | `docs/templates/ux/interaction-specification.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/ux/` containing `README.md` and 4 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/ux/README.md` and `docs/product/11-ux/README.md`.
2. Inspect authoritative canonical model `models/ux/ux.yaml`.
3. Copy the selected `.template.md` file to `docs/product/11-ux/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/11-ux/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/ux/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
