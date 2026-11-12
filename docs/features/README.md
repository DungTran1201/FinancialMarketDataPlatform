# Feature Documentation Packages (`docs/features/`)

## 1. Directory Purpose

`docs/features/` provides a modular workspace for self-contained, end-to-end feature documentation packages (adapted from the `docs/features/project-management/` pattern in `AgentHarnessBuilderTools`). When a major feature requires a cohesive multi-aspect specification bundle, it is organized under `docs/features/<feature-slug>/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Feature subdirectories `docs/features/<feature-slug>/` structured into the standard 11-document feature package.
- **Does NOT belong in this directory**: Global platform architecture (`docs/architecture/`), reusable templates (`docs/templates/`), or canonical YAML models (`models/`).

## 3. Agent Role and Responsibilities

Coordinated by `documentation-architect`, `requirements-engineer`, `architecture-modeler`, `ux-modeler`, `security-reviewer`, and `qa-reviewer`.

## 4. Authoritative Inputs

1. `work-items/<FEAT-ID>/artifact-plan.yaml` — Selects which feature package documents are required.
2. `models/` — Canonical models updated by the feature.
3. `docs/templates/` — Source templates for each document in the package.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `00-scope-assumptions-decisions.md` | Feature scope, assumptions, open questions & decisions | Required (per feature) | `docs/templates/discovery/discovery-report.template.md` |
| `01-feature-inventory-and-traceability.md` | Feature capability breakdown & traceability matrix | Required (per feature) | `docs/templates/requirements/traceability-matrix.template.md` |
| `02-srs.md` | Feature Software Requirements Specification | Required (per feature) | `docs/templates/requirements/SRS.template.md` |
| `03-use-cases-and-flows.md` | Use cases and business/user flows | Conditional | `docs/templates/use-cases/use-case-specification.template.md` |
| `04-domain-and-data-model.md` | Domain entities, aggregates & storage mapping | Conditional | `docs/templates/domain/domain-model.template.md` |
| `05-architecture-and-api-contracts.md` | Component design & endpoint contracts | Conditional | `docs/templates/api/API-contract.template.md` |
| `06-state-and-behavior.md` | State machines & sequence flows | Conditional | `docs/templates/behavior/state-machine.template.md` |
| `07-ux-and-screen-specs.md` | Information architecture & screen specifications | Conditional | `docs/templates/ux/screen-specification.template.md` |
| `08-security-and-threat-model.md` | STRIDE threats & security controls | Conditional | `docs/templates/security/threat-model.template.md` |
| `09-test-plan-and-cases.md` | Test plan and deterministic test cases (`TC-###`) | Required (per feature) | `docs/templates/testing/test-plan.template.md` |
| `10-implementation-readiness.md` | Gate checklist & readiness verification | Required (per feature) | `docs/templates/governance/definition-of-done.template.md` |

## 6. Directory and File Organization

Each feature resides in `docs/features/<kebab-feature-slug>/` with its own `README.md` and numbered documents selected via `artifact-plan.yaml`.

## 7. Document Creation Rules

Every feature folder must include an operational `README.md` and instantiate its documents from `docs/templates/`. Never create speculative feature folders until a `FEAT` work item is active.

## 8. Creation Workflow

1. Read `docs/features/README.md`.
2. Initialize a `FEAT-NNN` work item in `work-items/` and select required feature documents in `artifact-plan.yaml`.
3. Create `docs/features/<feature-slug>/README.md` and instantiate selected templates from `docs/templates/`.
4. Synchronize IDs with `models/` and `docs/product/`.
5. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Bridges cross-phase product artifacts (`docs/product/00..14`) for a specific feature delivery unit.

## 10. Quality Gate

Every feature subdirectory has a compliant `README.md`, uses registered IDs, and passes `validate_docs.py` and `validate_readmes.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT create populated Website feature folders during Phase 0 framework initialization.
- Do NOT treat a feature folder as an excuse to bypass canonical model updates in `models/`.
