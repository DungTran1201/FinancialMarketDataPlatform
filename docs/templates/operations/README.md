# Operations & DevOps Templates (`docs/templates/operations/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `13-operations`, targeting `docs/product/13-operations/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `operations` documentation (`deployment-guide.template.md, runbook.template.md, monitoring-specification.template.md, recovery-plan.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/13-operations/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `architecture-modeler`; review role: `security-reviewer`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/13-operations/README.md` — Target lifecycle phase operating contract.
3. `models/deployment/deployment.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `deployment-guide.template.md` | Deployment & Environment Configuration Guide (`OPS-DEP-[NNN]`) | Required | `docs/templates/operations/deployment-guide.template.md` |
| `runbook.template.md` | Operational Incident Runbook (`OPS-RUN-[NNN]`) | Required | `docs/templates/operations/runbook.template.md` |
| `monitoring-specification.template.md` | Monitoring, Metrics & Alerting Specification (`OPS-MON-[NNN]`) | Required | `docs/templates/operations/monitoring-specification.template.md` |
| `recovery-plan.template.md` | Backup, Replay & Disaster Recovery Plan (`OPS-REC-[NNN]`) | Required | `docs/templates/operations/recovery-plan.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/operations/` containing `README.md` and 4 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/operations/README.md` and `docs/product/13-operations/README.md`.
2. Inspect authoritative canonical model `models/deployment/deployment.yaml`.
3. Copy the selected `.template.md` file to `docs/product/13-operations/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/13-operations/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/operations/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
