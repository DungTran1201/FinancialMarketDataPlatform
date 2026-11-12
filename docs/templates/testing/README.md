# Testing & QA Templates (`docs/templates/testing/`)

## 1. Directory Purpose

Provides reusable markdown templates for lifecycle phase `12-testing`, targeting `docs/product/12-testing/` and feature packages in `docs/features/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: Reusable `*.template.md` files for `testing` documentation (`test-strategy.template.md, test-plan.template.md, test-case.template.md, test-report.template.md`).
- **Does NOT belong in this directory**: Populated project documents (which must be saved in `docs/product/12-testing/` or `docs/features/`).

## 3. Agent Role and Responsibilities

Primary authoring role: `qa-reviewer`; review role: `documentation-auditor`.

## 4. Authoritative Inputs

1. `docs/templates/README.md` — Master template library contract.
2. `docs/product/12-testing/README.md` — Target lifecycle phase operating contract.
3. `models/testing/testing.yaml` — Associated canonical model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `test-strategy.template.md` | Test Strategy & Verification Pyramid (`QA-STRAT-[NNN]`) | Required | `docs/templates/testing/test-strategy.template.md` |
| `test-plan.template.md` | Feature / Release Test Plan (`QA-PLAN-[NNN]`) | Required | `docs/templates/testing/test-plan.template.md` |
| `test-case.template.md` | Detailed Test Case Specification (`QA-TC-[NNN]`) | Required | `docs/templates/testing/test-case.template.md` |
| `test-report.template.md` | Test Execution & Verification Report (`QA-REP-[NNN]`) | Required | `docs/templates/testing/test-report.template.md` |

## 6. Directory and File Organization

Flat directory `docs/templates/testing/` containing `README.md` and 4 `.template.md` files.

## 7. Document Creation Rules

Instantiate templates into the target phase directory, assign a stable ID from `.agents/config/identifier-registry.yaml`, and preserve all `[MANDATORY]` sections.

## 8. Creation Workflow

1. Read `docs/templates/testing/README.md` and `docs/product/12-testing/README.md`.
2. Inspect authoritative canonical model `models/testing/testing.yaml`.
3. Copy the selected `.template.md` file to `docs/product/12-testing/`.
4. Populate verified facts and explicitly tag assumptions/open questions.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Mapped to `docs/product/12-testing/` in `.agents/config/document-map.yaml`.

## 10. Quality Gate

All templates in this folder pass `validate_templates.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT edit files inside `docs/templates/testing/` to hold feature-specific data.
- Do NOT invent unverified requirements when instantiating these templates.
