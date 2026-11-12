# Phase 11 — UX Information Architecture & Screen Specifications (`docs/product/11-ux/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 11 — UX Information Architecture & Screen Specifications** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `11-ux` specifications instantiated from `docs/templates/ux/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/ux/ux.yaml`), diagrams (`docs/diagrams/ux/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `ux-modeler` (`.agents/agents/ux-modeler.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/ux/ux.yaml` — Canonical model for this phase.
3. `docs/templates/ux/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `information-architecture.md` | Site map, route hierarchy & role visibility | Conditional | `docs/templates/ux/information-architecture.template.md` |
| `user-flows.md` | End-to-end user journey flows (`UX-###`) | Conditional | `docs/templates/ux/user-flow.template.md` |
| `screen-specifications.md` | Screen contracts (`SCR-###`), states & data bindings | Conditional | `docs/templates/ux/screen-specification.template.md` |

## 6. Directory and File Organization

Directory `docs/product/11-ux/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/ux/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/11-ux/README.md` and `docs/templates/ux/README.md`.
2. Inspect upstream canonical model `models/ux/ux.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/ux/` into `docs/product/11-ux/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/ux/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/ux/ux.yaml`, uses templates from `docs/templates/ux/`, and links to diagrams in `docs/diagrams/ux/`.

## 10. Quality Gate

All created artifacts in `docs/product/11-ux/` conform to `docs/templates/ux/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
