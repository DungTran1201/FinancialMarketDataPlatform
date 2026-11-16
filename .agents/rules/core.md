# Core Operating & Discovery-First Rule (`RULE-001`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-001` |
| **Rule Slug** | `core` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Mandates the Documentation V2 discovery workflow (`AGENTS.md` -> `docs/README.md` -> `docs/docs-index.yaml` -> Plane -> Domain -> `capability.yaml`), task-scoped selective loading, and strict separation of verified facts from assumptions and open blockers.

## 2. Mandatory Directives

1. **Mandatory Discovery Chain**: Follow the reading order in `AGENTS.md` and `docs/governance/standards/ai-agent-and-discovery-standards.md` before modifying any specification, contract, or code. When invoking a skill, read `.agents/skills/<skill>/SKILL.md` directly.
2. **Task-Scoped Selective Loading**: Load the active Role's **Primary** skill/rule plus only the **Task-Scoped** skills and rules needed for the Plane, Domain, and Capability touched by the task.
3. **Code-First Reality Verification**: Inspect actual files in `src/`, `frontend/`, `deploy/`, `tests/`, and `pyproject.toml` before stating `AS-IS` implemented behavior.
4. **Evidence & Uncertainty Discipline**: Tag unconfirmed hypotheses `[ASSUMPTION]` and log missing decisions/policies as `OPEN`, `NEEDS_CLARIFICATION`, or `BLOCKED` in `capability.yaml`.
5. **Deterministic Verification**: Run `scripts/docs/validate_docs.py` (or `tools/validators/run_all.py`) after modifying documentation or `.agents/` artifacts.

## 3. Prohibited Actions

- Never create parallel or duplicate documentation roots (`docs/archive/`, detached `docs/diagrams/`, standalone `models/` or `work-items/`).
- Never fabricate requirements, operational SLAs, test outputs, or runtime behavior.
- Never silently resolve contradictory or unapproved specifications without logging the conflict.

## 4. Verification Mechanism

- `scripts/docs/validate_docs.py` and `tests/docs/test_validate_docs.py`.
