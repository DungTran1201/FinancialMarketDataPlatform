# Phase 00 — Product & Domain Discovery (`docs/product/00-discovery/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 00 — Product & Domain Discovery** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `00-discovery` specifications instantiated from `docs/templates/discovery/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/context/system-context.yaml`), diagrams (`docs/diagrams/context/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `discovery-analyst` (`.agents/agents/discovery-analyst.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/context/system-context.yaml` — Canonical model for this phase.
3. `docs/templates/discovery/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `discovery-report.md` | Current-state & stakeholder discovery report | Conditional | `docs/templates/discovery/discovery-report.template.md` |
| `evidence-register.md` | FACT / ASSUMPTION / DECISION / OPEN QUESTION log | Required (when Phase 00 active) | `docs/templates/discovery/evidence-register.template.md` |
| `assumptions.md` | Working assumptions requiring validation | Required (when Phase 00 active) | `docs/templates/discovery/assumptions.template.md` |
| `open-questions.md` | Unresolved product/business questions | Required (when Phase 00 active) | `docs/templates/discovery/open-questions.template.md` |

## 6. Directory and File Organization

Directory `docs/product/00-discovery/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/discovery/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/00-discovery/README.md` and `docs/templates/discovery/README.md`.
2. Inspect upstream canonical model `models/context/system-context.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/discovery/` into `docs/product/00-discovery/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/context/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/context/system-context.yaml`, uses templates from `docs/templates/discovery/`, and links to diagrams in `docs/diagrams/context/`.

## 10. Quality Gate

All created artifacts in `docs/product/00-discovery/` conform to `docs/templates/discovery/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
