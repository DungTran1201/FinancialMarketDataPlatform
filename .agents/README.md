# Agent Workspace Configuration (`.agents/`)

This directory defines the greenfield agent rules, phase workflows, skills, and automated validation hooks for branch `greenfield/main`.

## Inspection & Replacement of Legacy V2 Validator (`DEC-P0-001` Compliance)

Prior to creating `greenfield/main`, the legacy `.agents/hooks.json` and `scripts/docs/validate_docs.py` (Documentation V2 validator) were inspected directly:
- **Incompatibilities Found**:
  1. Legacy `validate_docs.py` hardcodes legacy V2 index paths (`docs/docs-index.yaml` referencing `src/ingestion`, `src/serving`, `src/intelligence`), `docs/governance/catalog/artifact-catalog.yaml`, and V2 `capability.yaml` manifests across legacy planes (`data-plane`, `application-plane`, `intelligence-plane`).
  2. Reusing those files directly would force copying legacy V2 governance trees and domain taxonomy into `greenfield/main`, violating the clean-room isolation rule (`DEC-P0-001`).
  3. Legacy `pre_command_guard.py` lacked branch-protection guards for legacy Git branches (`main`, `feat/data-plane-production-delivery`), and `.agents/hooks.json` relied on bare `python` (which resolves to Python `3.8` on this Windows host rather than `.venv` Python `3.12`).
- **Resolution**:
  - Replaced with [tools/validators/validate_greenfield.py](../tools/validators/validate_greenfield.py) wired via [tools/validators/run_all.py](../tools/validators/run_all.py) and [hooks.json](hooks.json) (`PostToolUse` active, never disabled).
  - Enforces greenfield metadata headers (§6.3), mandatory directory `README.md` (§6.2), zero legacy directory leakage, Mermaid integrity, broken link/anchor checks, and Work-Item schema compliance (§9).

## Contents

- [hooks.json](hooks.json) — `PreToolUse`, `PostToolUse`, and `Stop` lifecycle hook bindings.
- [rules/greenfield-engineering-rules.md](rules/greenfield-engineering-rules.md) — Non-negotiable architecture, hardware, quant, and UI rules.
- [workflows/phase-lifecycle.md](workflows/phase-lifecycle.md) — Controlled Phase 0–9 progression and Work-Item state transitions.
- [skills/phase-gate-review/SKILL.md](skills/phase-gate-review/SKILL.md) — Operational procedure for verifying Phase Gates and PoC evidence.
