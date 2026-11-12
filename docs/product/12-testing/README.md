# Phase 12 — QA Test Strategy, Plans & Test Cases (`docs/product/12-testing/`)

## 1. Directory Purpose

Authoritative documentation space for **Phase 12 — QA Test Strategy, Plans & Test Cases** within the 15-phase product lifecycle (`docs/product/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Phase `12-testing` specifications instantiated from `docs/templates/testing/`.
- **Does NOT belong in this directory**: Canonical YAML models (`models/testing/testing.yaml`), diagrams (`docs/diagrams/sequence/`), or shared Data Platform baselines (`docs/architecture/`, `docs/specifications/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `qa-reviewer` (`.agents/agents/qa-reviewer.md`); audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/README.md` — Product lifecycle overview.
2. `models/testing/testing.yaml` — Canonical model for this phase.
3. `docs/templates/testing/README.md` — Template usage rules for this phase.
4. `docs/specifications/` & `docs/architecture/` — Shared platform contracts and constraints.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `test-strategy.md` | Testing pyramid & verification strategy | Conditional | `docs/templates/testing/test-strategy.template.md` |
| `test-plan.md` | Release / feature test plan | Conditional | `docs/templates/testing/test-plan.template.md` |
| `test-cases.md` | Deterministic test cases (`TC-###`) | Conditional | `docs/templates/testing/test-case.template.md` |

## 6. Directory and File Organization

Directory `docs/product/12-testing/` containing `README.md` and phase artifacts selected via `work-items/<ID>/artifact-plan.yaml`.

## 7. Document Creation Rules

Instantiate all documents from `docs/templates/testing/`, assign stable IDs from `.agents/config/identifier-registry.yaml` (using `WEB-*` prefixes where disambiguation from Data Platform IDs is needed), and keep status as `DRAFT` until reviewed.

## 8. Creation Workflow

1. Read `docs/product/12-testing/README.md` and `docs/templates/testing/README.md`.
2. Inspect upstream canonical model `models/testing/testing.yaml` and shared platform specs.
3. Copy the required template from `docs/templates/testing/` into `docs/product/12-testing/`.
4. Populate verified facts, tag any `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`, and update traceability.
5. Synchronize any derived diagrams in `docs/diagrams/sequence/`.
6. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Consumes structured data from `models/testing/testing.yaml`, uses templates from `docs/templates/testing/`, and links to diagrams in `docs/diagrams/sequence/`.

## 10. Quality Gate

All created artifacts in `docs/product/12-testing/` conform to `docs/templates/testing/` metadata standards and pass `validate_docs.py` and `validate_traceability.py`.

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
