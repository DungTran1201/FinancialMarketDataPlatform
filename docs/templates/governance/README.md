# Documentation Governance Templates (`docs/templates/governance/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `14-governance`, targeting `docs/product/14-governance/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `governance` documentation (`documentation-baseline.template.md, artifact-status.template.md, decision-log.template.md, definition-of-done.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/14-governance/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `documentation-auditor`; review role: `documentation-architect`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/14-governance/README.md` — Target lifecycle phase operating contract.
3. `models/requirements/requirements.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `documentation-baseline.template.md` | Documentation Baseline & Architecture Register (`GOV-BASE-[NNN]`) | Required | `docs/templates/governance/documentation-baseline.template.md` |
| `artifact-status.template.md` | Artifact Status & Lifecycle Register (`GOV-STAT-[NNN]`) | Required | `docs/templates/governance/artifact-status.template.md` |
| `decision-log.template.md` | Engineering & Product Decision Log (`GOV-DEC-[NNN]`) | Required | `docs/templates/governance/decision-log.template.md` |
| `definition-of-done.template.md` | Engineering & Documentation Definition of Done (DoD) (`GOV-DOD-[NNN]`) | Required | `docs/templates/governance/definition-of-done.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/governance/` containing `README.md` and 4 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/governance/README.md` and `docs/product/14-governance/README.md`.
2. Inspect authoritative canonical model `models/requirements/requirements.yaml`.
3. Copy the selected `.template.md` file to `docs/product/14-governance/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/14-governance/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/governance/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
