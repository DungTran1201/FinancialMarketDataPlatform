# Canonical Machine-Readable Models (`models/`)

## 1. Directory Purpose

`models/` is the authoritative structured YAML layer for `FinancialMarketDataPlatform`. It stores machine-readable models and reusable `.template.yaml` schemas across 12 engineering domains, serving as the structured source of truth for human-readable specifications (`docs/`) and visual diagrams (`docs/diagrams/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: 12 domain subdirectories (`requirements/`, `process/`, `context/`, `architecture/`, `domain/`, `api/`, `interaction/`, `state/`, `security/`, `ux/`, `testing/`, `deployment/`), their `README.md` contracts, `*.template.yaml` schemas, and `*.yaml` canonical models.
- **Does NOT belong in this directory**: Long-form narrative explanations (`docs/`), Mermaid files (`docs/diagrams/`), or work-item logs (`work-items/`).

## 3. Agent Role and Responsibilities

Updated by domain-specific modeling Agents (`requirements-engineer`, `process-modeler`, `architecture-modeler`, `domain-modeler`, `api-architect`, `ux-modeler`, `security-reviewer`, `qa-reviewer`) and audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root operating contract and source-of-truth hierarchy.
2. `.agents/rules/models.md` — Canonical model governance rule.
3. `.agents/config/identifier-registry.yaml` — Canonical ID prefixes and patterns.
4. `.agents/config/status-lifecycle.yaml` — Allowed model statuses.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `requirements/` | Canonical Requirements Models (`models/requirements/`) | Required | `models/requirements/README.md` |
| `process/` | Canonical Business & Data Process Models (`models/process/`) | Required | `models/process/README.md` |
| `context/` | Canonical System Context & Actor Models (`models/context/`) | Required | `models/context/README.md` |
| `architecture/` | Canonical Architecture & Component Models (`models/architecture/`) | Required | `models/architecture/README.md` |
| `domain/` | Canonical DDD Domain, Entity & Aggregate Models (`models/domain/`) | Required | `models/domain/README.md` |
| `api/` | Canonical API & Integration Contract Models (`models/api/`) | Required | `models/api/README.md` |
| `interaction/` | Canonical Sequence & Interaction Models (`models/interaction/`) | Required | `models/interaction/README.md` |
| `state/` | Canonical State Machine Models (`models/state/`) | Required | `models/state/README.md` |
| `security/` | Canonical Security & Threat Models (`models/security/`) | Required | `models/security/README.md` |
| `ux/` | Canonical UX, Information Architecture & Screen Models (`models/ux/`) | Required | `models/ux/README.md` |
| `testing/` | Canonical Testing & Verification Models (`models/testing/`) | Required | `models/testing/README.md` |
| `deployment/` | Canonical Deployment & Runtime Topology Models (`models/deployment/`) | Required | `models/deployment/README.md` |

## 6. Directory and File Organization

12 subdirectories, each containing an operational `README.md`, a `<domain>.template.yaml` schema, and one or more canonical `*.yaml` files.

## 7. Document Creation Rules

Every YAML file in `models/` must declare `version: "1.0"` and a `metadata` dictionary containing `model_id`, `name`, `description`, `status`, `canonical_model`, `created_at`, `updated_at`, `owner`, and `source_documents`.

## 8. Creation Workflow

1. Read `models/README.md` and the target subdirectory `models/<domain>/README.md`.
2. Inspect upstream approved requirements/ADRs and the active work item's `artifact-plan.yaml`.
3. Allocate stable IDs conforming to `.agents/config/identifier-registry.yaml`.
4. Update the canonical `.yaml` file first before synchronizing downstream prose (`docs/`) and diagrams (`docs/diagrams/`).
5. Run `tools/validators/validate_models.py` and `tools/validators/validate_identifiers.py`.

## 9. Relationships and Dependencies

Upstream structured source for `docs/product/`, `docs/architecture/`, `docs/specifications/`, and `docs/diagrams/`.

## 10. Quality Gate

All YAML files parse cleanly, contain mandatory `metadata` keys, use valid registered IDs, and pass `validate_models.py` and `validate_traceability.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT populate speculative Website product entities or requirements as `APPROVED` or `BASELINED`.
- Do NOT force unrelated domains into a single generic YAML file.
- Do NOT delete or renumber existing baselined IDs (`FR-01..10`, `ADR-001..006`).
