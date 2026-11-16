# Workspace Lifecycle Hooks (`tools/hooks/`)

Provides deterministic PreToolUse, PostToolUse, and Stop hook scripts registered in `.agents/hooks.json`.

## Active Hook Scripts

- `pre_command_guard.py`: PreToolUse shell guard checking for destructive command patterns.
- `post_doc_write_check.py`: PostToolUse hook invoking `scripts/docs/validate_docs.py`.
- `stop_readiness_check.py`: Stop hook delegating to `tools/validators/run_all.py` (`scripts/docs/validate_docs.py`).
