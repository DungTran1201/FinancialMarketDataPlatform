# Agent Workspace Integration (`.agents/`)

This directory configures local Agent execution hooks wired into Documentation V2. Legacy V1 multi-directory rules, model schemas, and work-item templates were retired during **Documentation V2 — Phase 1: Documentation Foundation** (preserved in Git tag `docs-v1-legacy-2026-11-16`).

## Authoritative Entrypoints

- **Agent Operating Contract**: [../AGENTS.md](../AGENTS.md)
- **Documentation Root**: [../docs/README.md](../docs/README.md)
- **Machine-Readable Docs Index**: [../docs/docs-index.yaml](../docs/docs-index.yaml)
- **AI Agent & Discovery Standards**: [../docs/governance/standards/ai-agent-and-discovery-standards.md](../docs/governance/standards/ai-agent-and-discovery-standards.md)

## Active Configuration

- [hooks.json](hooks.json): Registers `pre_command_guard.py`, `post_doc_write_check.py`, and `stop_readiness_check.py` (delegating documentation verification to `scripts/docs/validate_docs.py` via `tools/validators/run_all.py`).
