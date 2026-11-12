# Workspace Lifecycle Hooks (`tools/hooks/`)

## 1. Directory Purpose

Provides deterministic PreToolUse, PostToolUse, and Stop hook scripts wired into `.agents/hooks.json`.

## 2. Scope and Boundaries

- **Belongs in this directory**: 4 Python hook scripts (`pre_command_guard.py`, `post_doc_write_check.py`, `post_model_write_check.py`, `stop_readiness_check.py`) and `README.md`.
- **Does NOT belong in this directory**: Core validator logic (which lives in `tools/validators/`).

## 3. Agent Role and Responsibilities

Managed by `documentation-architect` and `security-reviewer`.

## 4. Authoritative Inputs

1. `.agents/hooks.json` — Hook trigger configuration.
2. `tools/validators/` — Underlying validation scripts.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `pre_command_guard.py` | PreToolUse guard inspecting shell commands for destructive operations | Required | `tools/hooks/pre_command_guard.py` |
| `post_doc_write_check.py` | PostToolUse hook running `validate_docs.py` and `validate_readmes.py` after doc edits | Required | `tools/hooks/post_doc_write_check.py` |
| `post_model_write_check.py` | PostToolUse hook running `validate_models.py` and `validate_identifiers.py` after YAML model edits | Required | `tools/hooks/post_model_write_check.py` |
| `stop_readiness_check.py` | Stop hook verifying work-item readiness and running `run_all.py` | Required | `tools/hooks/stop_readiness_check.py` |

## 6. Directory and File Organization

Flat directory `tools/hooks/` containing `README.md` and 4 hook scripts.

## 7. Document Creation Rules

Hooks must complete within `<10 seconds`, be conservative and deterministic, and delegate structural checks to `tools/validators/`.

## 8. Creation Workflow

1. Read `tools/hooks/README.md` and `.agents/hooks.json`.
2. Ensure every command path in `.agents/hooks.json` resolves to an existing script in `tools/hooks/`.
3. Verify via `tools/validators/validate_agent_config.py`.

## 9. Relationships and Dependencies

Referenced by `.agents/hooks.json` and invokes `tools/validators/`.

## 10. Quality Gate

All 4 hook scripts exist, are valid Python, and match `.agents/hooks.json`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT place slow network calls or LLM invocations inside workspace hooks.
