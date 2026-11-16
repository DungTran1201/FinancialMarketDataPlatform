# Documentation Tooling Compatibility Layer (`tools/`)

`tools/` preserves backwards-compatible CLI and lifecycle hook entrypoints used by `.github/workflows/ci.yml`, `run.bat`, `setup.bat`, and `.agents/hooks.json`, delegating core documentation validation directly to `scripts/docs/validate_docs.py`.

## Contents

- [validators/README.md](validators/README.md): Compatibility wrapper (`run_all.py`) invoking Documentation V2 validation.
- [hooks/README.md](hooks/README.md): Lifecycle hooks (`pre_command_guard.py`, `post_doc_write_check.py`, `stop_readiness_check.py`).
