# Documentation Engineering & Governance Automation (`tools/`)

## 1. Directory Purpose

`tools/` houses the deterministic validation suite (`tools/validators/`) and workspace lifecycle hooks (`tools/hooks/`) that enforce structural, metadata, identifier, README coverage, model schema, diagram, work-item, and traceability invariants across `FinancialMarketDataPlatform`.

## 2. Scope and Boundaries

- **Belongs in this directory**: `validators/` (11 Python validation scripts) and `hooks/` (4 lifecycle hook scripts).
- **Does NOT belong in this directory**: Application runtime code (`src/`), canonical models (`models/`), or documentation specs (`docs/`).

## 3. Agent Role and Responsibilities

Maintained by `documentation-architect` and executed by `documentation-auditor` and `qa-reviewer`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root operating contract.
2. `.agents/config/` — Machine-readable YAML registries (`document-map`, `artifact-matrix`, `identifier-registry`, `status-lifecycle`, `phase-gates`, `change-types`).
3. `.agents/hooks.json` — Hook registration configuration.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `validators/` | 10 specialized validators + `run_all.py` orchestrator | Required | `tools/validators/README.md` |
| `hooks/` | 4 PreToolUse, PostToolUse & Stop lifecycle hook scripts | Required | `tools/hooks/README.md` |

## 6. Directory and File Organization

Divided into `tools/validators/` and `tools/hooks/`.

## 7. Document Creation Rules

All scripts in `tools/` must be deterministic Python 3.12+ scripts using only standard library and `PyYAML`, returning exit code `0` on success and `1` on validation failure.

## 8. Creation Workflow

1. Read `tools/README.md`.
2. Run `python tools/validators/run_all.py` after any documentation, model, diagram, or work-item change.
3. Resolve any reported `[ERROR]` items before advancing work-item state.

## 9. Relationships and Dependencies

Validates `.agents/`, `docs/`, `models/`, `work-items/`, and `AGENTS.md`.

## 10. Quality Gate

`python tools/validators/run_all.py` exits with code `0` and reports `0` failed checks.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT introduce heavy external framework dependencies into `tools/`.
- Do NOT disable or stub out validation checks to mask broken documentation links or missing READMEs.
