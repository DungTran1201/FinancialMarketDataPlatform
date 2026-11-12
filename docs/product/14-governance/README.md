# Phase 14 — Documentation Governance, Status & Audit Baseline (`docs/product/14-governance/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 14 — Documentation Governance, Status & Audit Baseline** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `14-governance` specifications instantiated from `docs/templates/governance/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/requirements/requirements.yaml`), diagrams (`docs/diagrams/system/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `documentation-auditor` (`.agents/agents/documentation-auditor.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/requirements/requirements.yaml` — Canonical model for this phase.
3. `docs/templates/governance/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `documentation-baseline.md` | Master documentation architecture & baseline inventory | Required | `docs/templates/governance/documentation-baseline.template.md` |
| `artifact-status.md` | Lifecycle status register (`DRAFT`/`PROPOSED`/`BASELINED`) | Required | `docs/templates/governance/artifact-status.template.md` |
| `readme-coverage-matrix.md` | Complete directory README coverage verification matrix | Required | `docs/templates/governance/documentation-baseline.template.md` |
| `validation-report.md` | Automated validator execution report | Required | `docs/templates/testing/test-report.template.md` |
| `unresolved-issues.md` | Open questions, assumptions & deferred scope register | Required | `docs/templates/discovery/open-questions.template.md` |
| `decision-log.md` | Governance and documentation architecture decision log | Required | `docs/templates/governance/decision-log.template.md` |
| `definition-of-done.md` | Framework & work-item Definition of Done (DoD) | Required | `docs/templates/governance/definition-of-done.template.md` |

## 6. Directory and File Organization

Directory `docs/product/14-governance/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/governance/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/14-governance/README.md` and `docs/templates/governance/README.md`.
2. Inspect upstream canonical model `models/requirements/requirements.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/governance/` into `docs/product/14-governance/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/system/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/requirements/requirements.yaml`, uses templates from `docs/templates/governance/`, and links to diagrams in `docs/diagrams/system/`.

## 10. Quality Gate

All created artifacts in `docs/product/14-governance/` conform to `docs/templates/governance/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
