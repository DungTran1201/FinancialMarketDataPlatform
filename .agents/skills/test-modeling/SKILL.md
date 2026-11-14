---
name: test-modeling
description: Test plans and deterministic test cases (TC-###) in models/testing/.
---

# Skill: Test Strategy, Test Plan & Test Case Modeling (`SKILL-013`)

## 1. Description

Designs test strategies, test plans, and deterministic test cases (`TC-###`) in `models/testing/testing.yaml` and `docs/product/12-testing/`.

## 2. Trigger Conditions

- Phase `12-testing` or verification test case design (`qa-reviewer`).

## 3. Authoritative Inputs

- `models/testing/testing.yaml`, `models/requirements/acceptance-criteria.yaml`, `models/security/threats.yaml`, `tests/`, `docs/templates/testing/`.

## 4. Preconditions

1. Target `README.md` read; upstream `FR-###`, `AC-###`, and `CTRL-###` targets identified.

## 5. Execution Procedure

1. Update `models/testing/testing.yaml` first with `TC-###` IDs, test levels (`unit`, `contract`, `architecture`, `integration`), expected outcomes, and traced `FR-###`/`AC-###`/`CTRL-###` IDs.
2. Synchronize `docs/product/12-testing/` (`test-strategy.md`, `test-plan.md`, `test-cases.md`) using `docs/templates/testing/`.
3. Verify executable tests in `tests/` and run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `models/testing/testing.yaml`, `docs/product/12-testing/*.md`, `tests/**/*.py`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Block status promotion if any approved `AC-###` or `CTRL-###` lacks a linked `TC-###` in `validate_traceability.py`.

## 9. Restrictions

- Never mark unexecuted test cases as `PASSED` runtime evidence; never use live credentials in test suites.

## 10. Related Skills

- `data-platform-testing-recovery`, `traceability-audit`, `documentation-validation`
