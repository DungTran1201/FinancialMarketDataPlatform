---
name: documentation-validation
description: Executes scripts/docs/validate_docs.py, tools/validators/run_all.py, and tests/docs/ checks.
---

# Skill: Automated Documentation V2 Validation (`SKILL-016`)

## 1. Description

Executes the unified Documentation V2 validation suite (`scripts/docs/validate_docs.py`), its CI wrapper (`tools/validators/run_all.py`), and validator unit tests (`tests/docs/test_validate_docs.py`), triaging schema, metadata, applicability, link, Mermaid, contract, and traceability errors.

## 2. Trigger Conditions

- Mandatory final validation step after any modification to `docs/`, `AGENTS.md`, `.agents/`, `scripts/docs/`, or `tests/docs/` (`documentation-auditor` and all roles).

## 3. Authoritative Inputs

- `scripts/docs/validate_docs.py`, `tools/validators/run_all.py`, `tests/docs/test_validate_docs.py`, `docs/docs-index.yaml`, and `docs/governance/schemas/`.

## 4. Preconditions

1. Target `docs/` and `.agents/` files saved on disk and Python environment with `pyyaml` and `jsonschema` active.

## 5. Execution Procedure

1. Run `python scripts/docs/validate_docs.py` (and `python tools/validators/run_all.py` for CI wrapper parity).
2. Run `python -m pytest tests/docs/ -v` to confirm the validator unit/integration tests pass.
3. Triage any reported `[ERROR]` (`VAL-FM-001`, `VAL-CAP-MATRIX-001`, `VAL-LINK-001/002`, `VAL-DIAG-*`, `VAL-TRAC-*`, `VAL-ID-UNIQUE-001`, `VAL-TBD-001`) at its root source file.
4. Re-run until `scripts/docs/validate_docs.py` exits `0` with `0 errors`.

## 6. Output Artifacts

- Verified zero-error validator output from `scripts/docs/validate_docs.py` and `pytest tests/docs/ -v`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python tools/validators/run_all.py
python -m pytest tests/docs/ -v
```

## 8. Failure Handling

- Never ignore, bypass, or weaken validator checks to hide broken links, invalid frontmatter, or missing required artifacts.

## 9. Restrictions

- Do NOT invoke deleted V1 validator scripts (`validate_agent_config.py`, `validate_readmes.py`, `validate_models.py`, `validate_work_items.py`, `post_model_write_check.py`).

## 10. Related Skills

- `documentation-review`, `traceability-audit`, `documentation-creation`
