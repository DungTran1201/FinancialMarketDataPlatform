# Discovery Templates (`docs/templates/discovery/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `00-discovery`, targeting `docs/product/00-discovery/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `discovery` documentation (`discovery-report.template.md, evidence-register.template.md, assumptions.template.md, open-questions.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/00-discovery/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `discovery-analyst`; review role: `documentation-architect`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/00-discovery/README.md` — Target lifecycle phase operating contract.
3. `models/context/system-context.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `discovery-report.template.md` | Project & Domain Discovery Report (`DISC-REP-[NNN]`) | Required | `docs/templates/discovery/discovery-report.template.md` |
| `evidence-register.template.md` | Evidence & Fact Classification Register (`DISC-EVID-[NNN]`) | Required | `docs/templates/discovery/evidence-register.template.md` |
| `assumptions.template.md` | Assumptions Register (`DISC-ASSUMP-[NNN]`) | Required | `docs/templates/discovery/assumptions.template.md` |
| `open-questions.template.md` | Open Questions & Blockers Register (`DISC-OQ-[NNN]`) | Required | `docs/templates/discovery/open-questions.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/discovery/` containing `README.md` and 4 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/discovery/README.md` and `docs/product/00-discovery/README.md`.
2. Inspect authoritative canonical model `models/context/system-context.yaml`.
3. Copy the selected `.template.md` file to `docs/product/00-discovery/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/00-discovery/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/discovery/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
