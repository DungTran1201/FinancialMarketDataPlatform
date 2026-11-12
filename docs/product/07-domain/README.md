# Phase 07 — Product Domain Model & Ubiquitous Language (`docs/product/07-domain/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 07 — Product Domain Model & Ubiquitous Language** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `07-domain` specifications instantiated from `docs/templates/domain/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/domain/domain.yaml`), diagrams (`docs/diagrams/domain/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `domain-modeler` (`.agents/agents/domain-modeler.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/domain/domain.yaml` — Canonical model for this phase.
3. `docs/templates/domain/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `domain-model.md` | Product bounded contexts & context map | Conditional | `docs/templates/domain/domain-model.template.md` |
| `entities.md` | Product domain entities (`DOM-###`) | Conditional | `docs/templates/domain/entity.template.md` |
| `aggregates.md` | Aggregate roots & transactional boundaries | Conditional | `docs/templates/domain/aggregate.template.md` |
| `domain-rules.md` | Domain invariants & validation rules | Conditional | `docs/templates/domain/domain-rules.template.md` |

## 6. Directory and File Organization

Directory `docs/product/07-domain/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/domain/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/07-domain/README.md` and `docs/templates/domain/README.md`.
2. Inspect upstream canonical model `models/domain/domain.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/domain/` into `docs/product/07-domain/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/domain/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/domain/domain.yaml`, uses templates from `docs/templates/domain/`, and links to diagrams in `docs/diagrams/domain/`.

## 10. Quality Gate

All created artifacts in `docs/product/07-domain/` conform to `docs/templates/domain/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
