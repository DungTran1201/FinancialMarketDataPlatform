# Standard Document Template Library (`docs/templates/`)

## 1. Directory Purpose

`docs/templates/` is the centralized, reusable document template library for `FinancialMarketDataPlatform`. It provides 56 standardized `.template.md` blueprints across 14 engineering categories corresponding to the 15-phase documentation lifecycle (`00-discovery` through `14-governance`).

## 2. Scope and Boundaries

- **Belongs in this directory**: 14 template category folders (`discovery/`, `planning/`, `requirements/`, `business-process/`, `use-cases/`, `architecture/`, `domain/`, `api/`, `behavior/`, `security/`, `ux/`, `testing/`, `operations/`, `governance/`) and their `.template.md` files.
- **Does NOT belong in this directory**: Populated project or feature documents (which belong in `docs/product/`, `docs/features/`, `docs/architecture/`, or `docs/specifications/`).

## 3. Agent Role and Responsibilities

Managed by `documentation-architect` and validated by `documentation-auditor` via `tools/validators/validate_templates.py`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating contract.
2. `.agents/config/document-map.yaml` — Phase-to-template mapping.
3. `.agents/rules/documentation.md` — Template governance rule.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `discovery/` | Discovery Templates (`docs/templates/discovery/`) | Required | `docs/templates/discovery/README.md` |
| `planning/` | Planning Templates (`docs/templates/planning/`) | Required | `docs/templates/planning/README.md` |
| `requirements/` | Requirements Engineering Templates (`docs/templates/requirements/`) | Required | `docs/templates/requirements/README.md` |
| `business-process/` | Business Process Templates (`docs/templates/business-process/`) | Required | `docs/templates/business-process/README.md` |
| `use-cases/` | Use Case Templates (`docs/templates/use-cases/`) | Required | `docs/templates/use-cases/README.md` |
| `architecture/` | Architecture Templates (`docs/templates/architecture/`) | Required | `docs/templates/architecture/README.md` |
| `domain/` | Domain Modeling Templates (`docs/templates/domain/`) | Required | `docs/templates/domain/README.md` |
| `api/` | API & Integration Contract Templates (`docs/templates/api/`) | Required | `docs/templates/api/README.md` |
| `behavior/` | Behavioral & Interaction Templates (`docs/templates/behavior/`) | Required | `docs/templates/behavior/README.md` |
| `security/` | Security & Threat Modeling Templates (`docs/templates/security/`) | Required | `docs/templates/security/README.md` |
| `ux/` | UX & Frontend Specification Templates (`docs/templates/ux/`) | Required | `docs/templates/ux/README.md` |
| `testing/` | Testing & QA Templates (`docs/templates/testing/`) | Required | `docs/templates/testing/README.md` |
| `operations/` | Operations & DevOps Templates (`docs/templates/operations/`) | Required | `docs/templates/operations/README.md` |
| `governance/` | Documentation Governance Templates (`docs/templates/governance/`) | Required | `docs/templates/governance/README.md` |

## 6. Directory and File Organization

14 subdirectories organized by engineering discipline, each containing an operational `README.md` and reusable `*.template.md` blueprints.

## 7. Document Creation Rules

Every `.template.md` file must include a `Document Metadata` table (`Document ID`, `Title`, `Version`, `Status`, `Authoring Role`, `Review Role`, `Created Date`, `Updated Date`, `Work Item Reference`, `Canonical Model Reference`, `Source References`), explicit `[MANDATORY]`, `[CONDITIONAL]`, or `[OPTIONAL]` section markers, and standard placeholders (`[TO BE COMPLETED]`, `[ASSUMPTION — REQUIRES VALIDATION]`, `[OPEN QUESTION]`, `[PROPOSED — NOT APPROVED]`).

## 8. Creation Workflow

1. Read `docs/templates/README.md` and the specific category `README.md`.
2. Copy the appropriate `.template.md` file to the target directory in `docs/product/<phase>/` or `docs/features/<slug>/`.
3. Rename the copied file removing `.template` and populate sections from verified canonical models and discovery evidence.
4. Keep `[OPEN QUESTION]` or `[ASSUMPTION — REQUIRES VALIDATION]` tags wherever facts are unconfirmed.
5. Run `tools/validators/validate_templates.py` and `tools/validators/validate_docs.py`.

## 9. Relationships and Dependencies

Serves as the structural blueprint for all documents created in `docs/product/00..14` and `docs/features/`.

## 10. Quality Gate

All 14 categories and 56 `.template.md` files exist, contain required metadata and placeholders, contain zero invented product requirements, and pass `validate_templates.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT write populated feature specifications inside `docs/templates/`.
- Do NOT hardcode fictional product requirements into template files.
- Do NOT delete `[MANDATORY]` metadata or traceability sections when instantiating a template.
