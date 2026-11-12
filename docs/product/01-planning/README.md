# Phase 01 — Engineering & Delivery Planning (`docs/product/01-planning/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 01 — Engineering & Delivery Planning** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `01-planning` specifications instantiated from `docs/templates/planning/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/requirements/requirements.yaml`), diagrams (`docs/diagrams/system/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `documentation-architect` (`.agents/agents/documentation-architect.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/requirements/requirements.yaml` — Canonical model for this phase.
3. `docs/templates/planning/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `project-plan.md` | Delivery milestones, gates & risk register | Conditional | `docs/templates/planning/project-plan.template.md` |
| `work-breakdown-structure.md` | WBS decomposition & critical path | Conditional | `docs/templates/planning/WBS.template.md` |
| `implementation-roadmap.md` | Phased product implementation roadmap | Conditional | `docs/templates/planning/implementation-roadmap.template.md` |

## 6. Directory and File Organization

Directory `docs/product/01-planning/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/planning/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/01-planning/README.md` and `docs/templates/planning/README.md`.
2. Inspect upstream canonical model `models/requirements/requirements.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/planning/` into `docs/product/01-planning/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/system/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/requirements/requirements.yaml`, uses templates from `docs/templates/planning/`, and links to diagrams in `docs/diagrams/system/`.

## 10. Quality Gate

All created artifacts in `docs/product/01-planning/` conform to `docs/templates/planning/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
