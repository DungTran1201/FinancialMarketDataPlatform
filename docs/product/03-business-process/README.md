# Phase 03 — Business Process & Workflow Modeling (`docs/product/03-business-process/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 03 — Business Process & Workflow Modeling** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `03-business-process` specifications instantiated from `docs/templates/business-process/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/process/processes.yaml`), diagrams (`docs/diagrams/process/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `process-modeler` (`.agents/agents/process-modeler.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/process/processes.yaml` — Canonical model for this phase.
3. `docs/templates/business-process/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `process-catalog.md` | Catalog of business processes (`WEB-PROC-###`) | Conditional | `docs/templates/business-process/process-catalog.template.md` |
| `process-model.md` | End-to-end process hierarchy & handoffs | Conditional | `docs/templates/business-process/process-model.template.md` |

## 6. Directory and File Organization

Directory `docs/product/03-business-process/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/business-process/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/03-business-process/README.md` and `docs/templates/business-process/README.md`.
2. Inspect upstream canonical model `models/process/processes.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/business-process/` into `docs/product/03-business-process/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/process/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/process/processes.yaml`, uses templates from `docs/templates/business-process/`, and links to diagrams in `docs/diagrams/process/`.

## 10. Quality Gate

All created artifacts in `docs/product/03-business-process/` conform to `docs/templates/business-process/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
