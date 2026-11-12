# Phase 09 — Behavioral Sequence & State Modeling (`docs/product/09-behavior/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 09 — Behavioral Sequence & State Modeling** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `09-behavior` specifications instantiated from `docs/templates/behavior/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/state/state-machines.yaml`), diagrams (`docs/diagrams/sequence/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `architecture-modeler` (`.agents/agents/architecture-modeler.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/state/state-machines.yaml` — Canonical model for this phase.
3. `docs/templates/behavior/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `sequence-diagrams.md` | Runtime interaction sequence specifications (`SEQ-###`) | Conditional | `docs/templates/behavior/sequence-diagram.template.md` |
| `state-machines.md` | Lifecycle state machine specifications (`STATE-###`) | Conditional | `docs/templates/behavior/state-machine.template.md` |

## 6. Directory and File Organization

Directory `docs/product/09-behavior/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/behavior/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/09-behavior/README.md` and `docs/templates/behavior/README.md`.
2. Inspect upstream canonical model `models/state/state-machines.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/behavior/` into `docs/product/09-behavior/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/sequence/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/state/state-machines.yaml`, uses templates from `docs/templates/behavior/`, and links to diagrams in `docs/diagrams/sequence/`.

## 10. Quality Gate

All created artifacts in `docs/product/09-behavior/` conform to `docs/templates/behavior/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
