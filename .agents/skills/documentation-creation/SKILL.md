---
name: documentation-creation
description: Authors template-governed docs and 12-section directory READMEs from docs/templates/.
---

# Skill: Template-Governed Documentation Authoring (`SKILL-002`)

## 1. Description

Authors and updates markdown specifications and 12-section operational directory `README.md` files strictly from `docs/templates/`.

## 2. Trigger Conditions

- Any phase requiring template-governed markdown authoring or directory `README.md` synchronization (`documentation-architect`).

## 3. Authoritative Inputs

- `AGENTS.md`, target `README.md`, `work-items/<ID>/artifact-plan.yaml`, `.agents/config/document-map.yaml`, `models/`, `docs/templates/`.

## 4. Preconditions

1. Target directory `README.md` read; canonical YAML model in `models/` updated first.

## 5. Execution Procedure

1. Lookup required template and upstream model in `.agents/config/document-map.yaml`.
2. Copy structure from `docs/templates/` (or 12-section README contract in `tools/validators/validate_readmes.py`).
3. Populate prose strictly from canonical `models/` and verified evidence (`FACT`), tagging `[ASSUMPTION — REQUIRES VALIDATION]` or `[OPEN QUESTION]`.
4. Ensure all directory files are listed in Section 5 (`Required Artifacts`) of the directory's `README.md`.
5. Run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- Template-compliant markdown specifications in `docs/` and 12-section `README.md` files.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Keep status `DRAFT`/`REVIEW_REQUIRED` if `[OPEN QUESTION]` remains; resolve all validator errors before finishing.

## 9. Restrictions

- Never author freeform documents bypassing `docs/templates/`; never overwrite baselined `docs/architecture/` or `docs/specifications/` without an active work item.

## 10. Related Skills

- `documentation-review`, `traceability-audit`, `documentation-validation`
