# Behavioral & Interaction Templates (`docs/templates/behavior/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `09-behavior`, targeting `docs/product/09-behavior/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `behavior` documentation (`sequence-diagram.template.md, state-machine.template.md, interaction-specification.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/09-behavior/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `architecture-modeler`; review role: `api-architect`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/09-behavior/README.md` — Target lifecycle phase operating contract.
3. `models/state/state-machines.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `sequence-diagram.template.md` | Interaction Sequence Specification (`BEH-SEQ-[NNN]`) | Required | `docs/templates/behavior/sequence-diagram.template.md` |
| `state-machine.template.md` | State Machine Specification (`BEH-STATE-[NNN]`) | Required | `docs/templates/behavior/state-machine.template.md` |
| `interaction-specification.template.md` | Cross-Component Interaction Specification (`BEH-INT-[NNN]`) | Required | `docs/templates/behavior/interaction-specification.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/behavior/` containing `README.md` and 3 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/behavior/README.md` and `docs/product/09-behavior/README.md`.
2. Inspect authoritative canonical model `models/state/state-machines.yaml`.
3. Copy the selected `.template.md` file to `docs/product/09-behavior/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/09-behavior/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/behavior/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
