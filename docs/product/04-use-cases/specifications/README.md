# Individual Use Case Specifications (`docs/product/04-use-cases/specifications/`)

## 1. Directory Purpose

Stores granular, one-file-per-use-case specifications (`WEB-UC-<DOMAIN>-<NNN>-<slug>.md`) for product and user workflows.

## 2. Scope and Boundaries

- **Belongs in this directory**: Individual Use Case specification markdown files instantiated from `docs/templates/use-cases/use-case-specification.template.md`.
- **Does NOT belong in this directory**: High-level actor catalogs (`../use-case-model.md`) or UML diagrams (`docs/diagrams/use-case/`).

## 3. Agent Role and Responsibilities

Authored by `requirements-engineer` and reviewed by `qa-reviewer` and `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/product/04-use-cases/README.md` — Parent phase contract.
2. `docs/product/02-requirements/` — Functional requirements (`WEB-FR-###`) and business rules (`WEB-BR-###`).
3. `docs/templates/use-cases/use-case-specification.template.md` — Mandatory template.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `WEB-UC-<DOMAIN>-<NNN>-<slug>.md` | Detailed Use Case specification | Conditional (per Use Case) | `docs/templates/use-cases/use-case-specification.template.md` |

## 6. Directory and File Organization

Flat directory `docs/product/04-use-cases/specifications/` with files named `WEB-UC-<DOMAIN>-<NNN>-<kebab-slug>.md`.

## 7. Document Creation Rules

Every Use Case file must use `use-case-specification.template.md` and define Preconditions, Trigger, Main Success Scenario, Alternative Flows, Exception Flows, Postconditions, Business Rules (`BR-###`), and Acceptance Criteria (`AC-###`).

## 8. Creation Workflow

1. Read `docs/product/04-use-cases/specifications/README.md`.
2. Confirm the Use Case ID in `docs/product/04-use-cases/use-case-catalog.md`.
3. Instantiate `docs/templates/use-cases/use-case-specification.template.md`.
4. Link steps to `WEB-FR-###`, `WEB-BR-###`, `API-###`, and `TC-###`.
5. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Links `docs/product/02-requirements/` to `docs/product/08-api/`, `docs/product/11-ux/`, and `docs/product/12-testing/`.

## 10. Quality Gate

Every Use Case specification has a unique `WEB-UC-*` ID and complete main/alternative/exception scenarios.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT create speculative Use Case files before product discovery and requirements intake.
- Do NOT omit exception flows or postconditions.
