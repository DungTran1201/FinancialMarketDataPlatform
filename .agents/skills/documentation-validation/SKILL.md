---
name: documentation-validation
description: Executes tools/validators/run_all.py and resolves structural or traceability errors.
---

# Skill: Automated Documentation & Model Validation (`SKILL-016`)

## 1. Description

Executes the 10-validator suite (`tools/validators/run_all.py`) and triages structural, README, model, diagram, identifier, or traceability errors.

## 2. Trigger Conditions

- Mandatory step 10 of `AGENTS.md` after any documentation, model, diagram, or `.agents/` change (`documentation-auditor` and all roles).

## 3. Authoritative Inputs

- `tools/validators/run_all.py` (`validate_agent_config.py`, `validate_artifact_matrix.py`, `validate_readmes.py`, `validate_templates.py`, `validate_models.py`, `validate_identifiers.py`, `validate_diagrams.py`, `validate_docs.py`, `validate_traceability.py`, `validate_work_items.py`).

## 4. Preconditions

1. Target canonical models (`models/`), docs (`docs/`), and directory `README.md` files saved on disk.

## 5. Execution Procedure

1. Run `python tools/validators/run_all.py`.
2. Triage any reported `[ERROR]` by inspecting the failing validator rule and fixing the upstream YAML model, markdown header, README section, or Mermaid block.
3. Re-run `python tools/validators/run_all.py` until all 10 validators exit with `0 error(s)`.

## 6. Output Artifacts

- Zero-error validation output and updated verification evidence in `work-items/<ID>/review.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Never ignore or suppress validator errors; fix the root artifact discrepancy before ending the turn.

## 9. Restrictions

- Never weaken validator checks in `tools/validators/` to hide broken links, missing README sections, or missing traceability.

## 10. Related Skills

- `documentation-review`, `traceability-audit`, `documentation-creation`
