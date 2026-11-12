# Phase 04 — Use Case Modeling & Specifications (`docs/product/04-use-cases/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 04 — Use Case Modeling & Specifications** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `04-use-cases` specifications instantiated from `docs/templates/use-cases/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/interaction/interactions.yaml`), diagrams (`docs/diagrams/use-case/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `requirements-engineer` (`.agents/agents/requirements-engineer.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/interaction/interactions.yaml` — Canonical model for this phase.
3. `docs/templates/use-cases/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `use-case-model.md` | Actor taxonomy & use case package overview | Conditional | `docs/templates/use-cases/use-case-model.template.md` |
| `use-case-catalog.md` | Index of Use Cases (`WEB-UC-###`) | Conditional | `docs/templates/use-cases/use-case-catalog.template.md` |
| `use-case-matrix.md` | Use Case to FR/API/Screen traceability matrix | Conditional | `docs/templates/use-cases/use-case-matrix.template.md` |
| `specifications/` | Individual detailed Use Case specifications | Conditional | `docs/product/04-use-cases/specifications/README.md` |

## 6. Directory and File Organization

Directory `docs/product/04-use-cases/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/use-cases/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/04-use-cases/README.md` and `docs/templates/use-cases/README.md`.
2. Inspect upstream canonical model `models/interaction/interactions.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/use-cases/` into `docs/product/04-use-cases/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/use-case/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/interaction/interactions.yaml`, uses templates from `docs/templates/use-cases/`, and links to diagrams in `docs/diagrams/use-case/`.

## 10. Quality Gate

All created artifacts in `docs/product/04-use-cases/` conform to `docs/templates/use-cases/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
