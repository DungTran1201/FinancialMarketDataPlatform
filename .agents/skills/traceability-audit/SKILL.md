---
name: traceability-audit
description: Audits bidirectional traceability across CAP, FR/NFR, UC, DOM/API, and TC.
---

# Skill: Bidirectional Traceability Audit (`SKILL-015`)

## 1. Description

Verifies end-to-end linkage across `CAP -> FR/NFR/BR -> UC/PROC -> DOM/COMP/API -> TC` and `THR -> CTRL -> TC`.

## 2. Trigger Conditions

- Phase `02-requirements`, `12-testing`, `14-governance`, or after modifying canonical IDs in `models/` (`documentation-auditor`, `requirements-engineer`, `qa-reviewer`).

## 3. Authoritative Inputs

- `models/requirements/`, `models/architecture/`, `models/domain/`, `models/api/`, `models/security/`, `models/testing/`, `docs/product/02-requirements/traceability-matrix.md`.

## 4. Preconditions

1. Target `README.md` read; all canonical YAML files in `models/` parse cleanly.

## 5. Execution Procedure

1. Execute `python tools/validators/validate_traceability.py` and `validate_identifiers.py`.
2. Verify every `FR-###` links to an `AC-###` and `TC-###`, and every `THR-###` links to a `CTRL-###` and `TC-###`.
3. Synchronize `docs/product/02-requirements/traceability-matrix.md` from `docs/templates/requirements/traceability-matrix.template.md`.
4. Run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `docs/product/02-requirements/traceability-matrix.md` and synchronized `models/**/*.yaml` cross-references.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Fix orphan IDs or broken cross-references in `models/` before completing the turn.

## 9. Restrictions

- Never fabricate dummy `TC-###` or `CTRL-###` entries without real test/control definitions; never delete preserved IDs (`FR-01..10`, `ADR-001..006`).

## 10. Related Skills

- `requirements-engineering`, `test-modeling`, `documentation-validation`
