# Phase 02 — Requirements Engineering Baseline (`docs/product/02-requirements/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 02 — Requirements Engineering Baseline** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `02-requirements` specifications instantiated from `docs/templates/requirements/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/requirements/requirements.yaml`), diagrams (`docs/diagrams/context/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `requirements-engineer` (`.agents/agents/requirements-engineer.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/requirements/requirements.yaml` — Canonical model for this phase.
3. `docs/templates/requirements/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `SRS.md` | IEEE-compatible Software Requirements Specification | Required (for product features) | `docs/templates/requirements/SRS.template.md` |
| `functional-requirements.md` | Normalized functional requirements (`WEB-FR-###`) | Required (for product features) | `docs/templates/requirements/functional-requirements.template.md` |
| `non-functional-requirements.md` | Product quality attributes (`WEB-NFR-###`) | Conditional | `docs/templates/requirements/non-functional-requirements.template.md` |
| `business-rules.md` | Deterministic business rules (`WEB-BR-###`) | Conditional | `docs/templates/requirements/business-rules.template.md` |
| `acceptance-criteria.md` | Given/When/Then criteria (`WEB-AC-###`) | Required (for product features) | `docs/templates/requirements/acceptance-criteria.template.md` |
| `traceability-matrix.md` | Bidirectional requirements traceability matrix | Required (for product features) | `docs/templates/requirements/traceability-matrix.template.md` |

## 6. Directory and File Organization

Directory `docs/product/02-requirements/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/requirements/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/02-requirements/README.md` and `docs/templates/requirements/README.md`.
2. Inspect upstream canonical model `models/requirements/requirements.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/requirements/` into `docs/product/02-requirements/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/context/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/requirements/requirements.yaml`, uses templates from `docs/templates/requirements/`, and links to diagrams in `docs/diagrams/context/`.

## 10. Quality Gate

All created artifacts in `docs/product/02-requirements/` conform to `docs/templates/requirements/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
