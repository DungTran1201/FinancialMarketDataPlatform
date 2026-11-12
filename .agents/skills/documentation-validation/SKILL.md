---
name: documentation-validation
description: Runs the deterministic validator suite (`tools/validators/run_all.py`) and triages structural or semantic errors.
---

# Skill: Automated Documentation & Model Validation (`SKILL-016`)

## 1. Description

Runs the deterministic validator suite (`tools/validators/run_all.py`) and triages structural or semantic errors.

## 2. Trigger Conditions

- Invoked when a Work Item in `work-items/<ID>/` requires `documentation-validation` activities during phase `14-governance`.
- Invoked by Agent role `documentation-auditor` (`.agents/agents/documentation-auditor.md`).

## 3. Authoritative Inputs

- `AGENTS.md` and target directory `README.md`
- Active Work Item (`work-items/<ID>/request.md`, `discovery.md`, `artifact-plan.yaml`)
- Relevant canonical models in `models/`
- Template reference: `tools/validators/`

## 4. Preconditions

1. Target directory `README.md` has been read in full.
2. Required upstream inputs have been inspected and classified (`FACT`, `ASSUMPTION`, `DECISION`, `OPEN QUESTION`).

## 5. Execution Procedure

1. Read the target directory `README.md` and verify scope boundaries.
2. Inspect upstream canonical models in `models/` and baseline specifications in `docs/`.
3. Select the designated template from `tools/validators/`.
4. Populate or update the canonical YAML model in `models/` first (where applicable) using stable IDs from `.agents/config/identifier-registry.yaml`.
5. Generate or synchronize the target markdown document and/or Mermaid diagram.
6. Explicitly tag any unconfirmed items with `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`.
7. Execute the automated validation suite (`tools/validators/run_all.py`).

## 6. Output Artifacts

- Updated canonical YAML model in `models/` (when applicable).
- Template-compliant markdown artifact in `docs/` or review output in `work-items/`.

## 7. Validation

```powershell
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 8. Failure Handling

- If required upstream facts are missing, record an `[OPEN QUESTION]` entry and keep artifact status as `DRAFT` or `REVIEW_REQUIRED`.
- If any validator fails, fix structural, metadata, or link errors before completing the turn.

## 9. Restrictions

- Never invent product requirements, endpoints, or business rules.
- Never overwrite baselined Data Platform files without an explicit work item action.

## 10. Related Skills

- `documentation-creation`
- `traceability-audit`
- `documentation-validation`
