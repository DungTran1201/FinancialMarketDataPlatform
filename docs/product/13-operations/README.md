# Phase 13 — Operations, Deployment & Runbooks (`docs/product/13-operations/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 13 — Operations, Deployment & Runbooks** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `13-operations` specifications instantiated from `docs/templates/operations/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/deployment/deployment.yaml`), diagrams (`docs/diagrams/deployment/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `architecture-modeler` (`.agents/agents/architecture-modeler.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/deployment/deployment.yaml` — Canonical model for this phase.
3. `docs/templates/operations/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `deployment-guide.md` | Environment & Docker Compose deployment guide | Conditional | `docs/templates/operations/deployment-guide.template.md` |
| `runbook.md` | Incident triage & recovery runbooks | Conditional | `docs/templates/operations/runbook.template.md` |
| `monitoring.md` | SLIs, Prometheus metrics & Grafana alerts | Conditional | `docs/templates/operations/monitoring-specification.template.md` |

## 6. Directory and File Organization

Directory `docs/product/13-operations/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/operations/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/13-operations/README.md` and `docs/templates/operations/README.md`.
2. Inspect upstream canonical model `models/deployment/deployment.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/operations/` into `docs/product/13-operations/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/deployment/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/deployment/deployment.yaml`, uses templates from `docs/templates/operations/`, and links to diagrams in `docs/diagrams/deployment/`.

## 10. Quality Gate

All created artifacts in `docs/product/13-operations/` conform to `docs/templates/operations/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT invent unverified product requirements or business rules.
- Do NOT duplicate shared Data Platform specifications from `docs/architecture/` or `docs/specifications/`.
- Do NOT mark any document containing `[TO BE COMPLETED]` or `[OPEN QUESTION]` as `APPROVED`.
