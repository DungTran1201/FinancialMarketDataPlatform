# Automated Documentation & Model Validators (`tools/validators/`)

## 1. Directory Purpose

Provides 10 deterministic Python validators plus `run_all.py` to verify every subsystem of the Documentation Engineering Framework.

## 2. Scope and Boundaries

- **Belongs in this directory**: 11 Python scripts (`validate_*.py` and `run_all.py`) and `README.md`.
- **Does NOT belong in this directory**: Lifecycle hook wrappers (`tools/hooks/`) or unit tests (`tests/`).

## 3. Agent Role and Responsibilities

Executed by all Agents prior to work-item gate completion; owned by `documentation-auditor`.

## 4. Authoritative Inputs

1. `.agents/config/document-map.yaml`
2. `.agents/config/artifact-matrix.yaml`
3. `.agents/config/identifier-registry.yaml`
4. `.agents/config/status-lifecycle.yaml`

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `validate_docs.py` | Verifies markdown titles, non-empty structure, and absence of unauthorized duplicate roots | Required | `tools/validators/validate_docs.py` |
| `validate_readmes.py` | Verifies 100% README coverage across all managed directories and checks all 12 mandatory sections | Required | `tools/validators/validate_readmes.py` |
| `validate_templates.py` | Verifies all 14 template categories, 57 `.template.md` files, metadata tables, and placeholders | Required | `tools/validators/validate_templates.py` |
| `validate_models.py` | Verifies YAML syntax, required `metadata` fields, and allowed statuses across `models/` | Required | `tools/validators/validate_models.py` |
| `validate_diagrams.py` | Verifies diagram directories, Mermaid code blocks, and diagram metadata/explanations | Required | `tools/validators/validate_diagrams.py` |
| `validate_traceability.py` | Verifies cross-references between `models/`, `docs/`, and `docs/diagrams/` | Required | `tools/validators/validate_traceability.py` |
| `validate_identifiers.py` | Verifies ID uniqueness, regex pattern compliance, and preservation of `FR-01..10` and `ADR-001..006` | Required | `tools/validators/validate_identifiers.py` |
| `validate_artifact_matrix.py` | Verifies `.agents/config/artifact-matrix.yaml` and `change-types.yaml` consistency | Required | `tools/validators/validate_artifact_matrix.py` |
| `validate_work_items.py` | Verifies `work-items/_template/` and active work items (`DOCS-001`) structure and state transitions | Required | `tools/validators/validate_work_items.py` |
| `validate_agent_config.py` | Verifies `AGENTS.md`, `.agents/agents/`, `rules/`, `skills/`, `config/`, `hooks.json`, and skill registries | Required | `tools/validators/validate_agent_config.py` |
| `run_all.py` | Master runner executing all 10 validators sequentially and printing a combined summary | Required | `tools/validators/run_all.py` |

## 6. Directory and File Organization

Flat directory `tools/validators/` containing `README.md`, 10 `validate_*.py` modules, and `run_all.py`.

## 7. Document Creation Rules

Each validator must be runnable standalone (`python tools/validators/<name>.py`), print clear `[PASS]` / `[ERROR]` diagnostics, and exit with `0` (pass) or `1` (fail).

## 8. Creation Workflow

1. Read `tools/validators/README.md`.
2. Execute `python tools/validators/run_all.py`.
3. If any validator exits non-zero, inspect its `[ERROR]` lines and fix the offending artifact.

## 9. Relationships and Dependencies

Invoked by `tools/hooks/`, CI workflows (`.github/workflows/ci.yml`), and Agent skills.

## 10. Quality Gate

All 10 validators execute cleanly in `<5 seconds` and return exit code `0`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT modify validators to ignore genuine errors.
- Do NOT allow validators to mutate repository files silently (validators are strictly read-only checkers).
