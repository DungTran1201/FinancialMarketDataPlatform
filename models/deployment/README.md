# Canonical Deployment & Runtime Topology Models (`models/deployment/`)

## 1. Directory Purpose

Stores the canonical machine-readable YAML models and `.template.yaml` schema for the `deployment` domain.

## 2. Scope and Boundaries

- **Belongs in this directory**: `deployment.template.yaml, deployment.yaml` and `README.md`.
- **Does NOT belong in this directory**: Narrative markdown documents (which belong in `docs/product/13-operations/` or `docs/architecture/12-deployment-architecture.md`).

## 3. Agent Role and Responsibilities

Primary owning Agent role: `architecture-modeler`; audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `models/README.md` — Canonical model subsystem contract.
2. `docs/architecture/12-deployment-architecture.md` — Shared platform specification reference.
3. `docs/product/13-operations/README.md` — Product lifecycle phase reference.
4. `.agents/config/identifier-registry.yaml` — Identifier format rules.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `deployment.template.yaml` | Reusable YAML model template | Required | `models/deployment/deployment.template.yaml` |
| `deployment.yaml` | Canonical `deployment` model | Required | `models/deployment/deployment.yaml` |

## 6. Directory and File Organization

Flat directory `models/deployment/` containing `README.md`, `deployment.template.yaml`, and canonical `*.yaml` model files.

## 7. Document Creation Rules

All YAML files must include `version: "1.0"` and the standard `metadata` block (`model_id`, `name`, `description`, `status`, `canonical_model`, `created_at`, `updated_at`, `owner`, `source_documents`).

## 8. Creation Workflow

1. Read `models/deployment/README.md` and inspect `deployment.template.yaml`.
2. Verify authoritative upstream evidence in the active Work Item.
3. Update the canonical YAML file(s) in `models/deployment/` preserving existing IDs.
4. Synchronize affected markdown docs in `docs/product/13-operations/` and diagrams in `docs/diagrams/`.
5. Run `tools/validators/validate_models.py` and `tools/validators/validate_traceability.py`.

## 9. Relationships and Dependencies

Provides structured entities and IDs consumed by `docs/product/13-operations/`, `docs/architecture/12-deployment-architecture.md`, and `docs/diagrams/`.

## 10. Quality Gate

All YAML files in `models/deployment/` pass `validate_models.py`, `validate_identifiers.py`, and `validate_readmes.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT modify `.template.yaml` to store feature-specific state.
- Do NOT introduce unregistered identifier prefixes or break cross-model references.
