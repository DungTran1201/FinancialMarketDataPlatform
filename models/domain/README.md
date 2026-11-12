# Canonical DDD Domain, Entity & Aggregate Models (`models/domain/`)

## 1. Directory Purpose

Stores the canonical machine-readable YAML models and `.template.yaml` schema for the `domain` domain.

## 2. Scope and Boundaries

- **Belongs in this directory**: `domain.template.yaml, domain.yaml, entities.yaml, aggregates.yaml` and `README.md`.
- **Does NOT belong in this directory**: Narrative markdown documents (which belong in `docs/product/07-domain/` or `docs/specifications/data-dictionary.md`).

## 3. Agent Role and Responsibilities

Primary owning Agent role: `domain-modeler`; audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `models/README.md` — Canonical model subsystem contract.
2. `docs/specifications/data-dictionary.md` — Shared platform specification reference.
3. `docs/product/07-domain/README.md` — Product lifecycle phase reference.
4. `.agents/config/identifier-registry.yaml` — Identifier format rules.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `domain.template.yaml` | Reusable YAML model template | Required | `models/domain/domain.template.yaml` |
| `domain.yaml` | Canonical `domain` model | Required | `models/domain/domain.yaml` |
| `entities.yaml` | Canonical `domain` model | Required | `models/domain/entities.yaml` |
| `aggregates.yaml` | Canonical `domain` model | Required | `models/domain/aggregates.yaml` |

## 6. Directory and File Organization

Flat directory `models/domain/` containing `README.md`, `domain.template.yaml`, and canonical `*.yaml` model files.

## 7. Document Creation Rules

All YAML files must include `version: "1.0"` and the standard `metadata` block (`model_id`, `name`, `description`, `status`, `canonical_model`, `created_at`, `updated_at`, `owner`, `source_documents`).

## 8. Creation Workflow

1. Read `models/domain/README.md` and inspect `domain.template.yaml`.
2. Verify authoritative upstream evidence in the active Work Item.
3. Update the canonical YAML file(s) in `models/domain/` preserving existing IDs.
4. Synchronize affected markdown docs in `docs/product/07-domain/` and diagrams in `docs/diagrams/`.
5. Run `tools/validators/validate_models.py` and `tools/validators/validate_traceability.py`.

## 9. Relationships and Dependencies

Provides structured entities and IDs consumed by `docs/product/07-domain/`, `docs/specifications/data-dictionary.md`, and `docs/diagrams/`.

## 10. Quality Gate

All YAML files in `models/domain/` pass `validate_models.py`, `validate_identifiers.py`, and `validate_readmes.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT modify `.template.yaml` to store feature-specific state.
- Do NOT introduce unregistered identifier prefixes or break cross-model references.
