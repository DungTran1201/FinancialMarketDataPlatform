# Phase 05 — System Analysis & Boundary Alignment (`docs/product/05-system-analysis/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 05 — System Analysis & Boundary Alignment** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `05-system-analysis` specifications instantiated from `docs/templates/architecture/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/context/system-context.yaml`), diagrams (`docs/diagrams/context/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `architecture-modeler` (`.agents/agents/architecture-modeler.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/context/system-context.yaml` — Canonical model for this phase.
3. `docs/templates/architecture/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `system-context.md` | Product-to-Data-Platform context boundary analysis | Conditional | `docs/templates/architecture/system-context.template.md` |

## 6. Directory and File Organization

Directory `docs/product/05-system-analysis/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/architecture/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/05-system-analysis/README.md` and `docs/templates/architecture/README.md`.
2. Inspect upstream canonical model `models/context/system-context.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/architecture/` into `docs/product/05-system-analysis/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/context/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/context/system-context.yaml`, uses templates from `docs/templates/architecture/`, and links to diagrams in `docs/diagrams/context/`.

## 10. Quality Gate

All created artifacts in `docs/product/05-system-analysis/` conform to `docs/templates/architecture/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
