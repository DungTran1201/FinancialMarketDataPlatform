---
name: test-modeling
description: Authors plane test plans, capability test-scenarios.md, and test-cases.yaml in Documentation V2.
---

# Skill: Test Strategy, Test Plan & Test Case Modeling (`SKILL-013`)

## 1. Description

Designs plane verification plans (`<plane>/operations/test-plan.md`), behavioral/fault test scenarios (`quality/test-scenarios.md`), and deterministic executable test case catalogs (`quality/test-cases.yaml`) linked to `quality/traceability.yaml`.

## 2. Trigger Conditions

- Lifecycle Stage 7 (`Verification`), Gate `QG-6-VERIFY`, or capability test coverage updates (`qa-reviewer`, `qa-lead`).

## 3. Authoritative Inputs

- `docs/governance/standards/qa-and-testing-standards.md`, `docs/governance/templates/quality/`, owning `capability.yaml`, `<capability>/requirements/`, `<capability>/security/`, and `tests/`.

## 4. Preconditions

1. Owning `capability.yaml` read and upstream `FR-*`, `NFR-*`, `RULE-*`, and `SEC-*` IDs enumerated.

## 5. Execution Procedure

1. Author or update `<capability>/quality/test-scenarios.md` (`TS-*`) and `<capability>/quality/test-cases.yaml` (`TC-*`) from `docs/governance/templates/quality/`.
2. Map each `TC-*` to real test file paths in `tests/` or `frontend/tests/` (or explicitly mark missing/blocked tests in `verification_evidence` and `capability.yaml`).
3. Maintain `<plane>/operations/test-plan.md` with clear environment boundaries (in-process/simulated vs live container execution).
4. Synchronize `quality/traceability.yaml` and run `python scripts/docs/validate_docs.py` plus executable test suites.

## 6. Output Artifacts

- `<plane>/operations/test-plan.md`, `<capability>/quality/{test-plan.md,test-scenarios.md,test-cases.yaml,traceability.yaml}`, and automated tests under `tests/`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/ -v
```

## 8. Failure Handling

- Record missing test suites or environment limitations honestly; never mark `implementation_status: VERIFIED` without passing execution logs.

## 9. Restrictions

- Never fabricate test results or cite unexecuted suites as passed; never use live credentials in tests; never recreate V1 `models/testing/`.

## 10. Related Skills

- `data-platform-testing-recovery`, `traceability-audit`, `documentation-validation`
