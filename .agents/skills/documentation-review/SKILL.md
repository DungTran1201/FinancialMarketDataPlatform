---
name: documentation-review
description: Audits applicability, placeholder hygiene, gates QG-1..QG-7, and approval readiness in V2.
---

# Skill: Documentation Quality & Gate Audit (`SKILL-014`)

## 1. Description

Audits Documentation V2 completeness, risk-tier applicability compliance (`artifact-applicability-matrix.yaml`), placeholder hygiene, `AS-IS vs TARGET` honesty, and quality gate criteria (`QG-1-SCOPE`..`QG-7-OPS`) before `status: APPROVED` transitions.

## 2. Trigger Conditions

- Lifecycle Stage 5 (`Review and Approval`), Gate `QG-5-APPROVAL`, or PR documentation audits (`documentation-auditor`, `documentation-architect`).

## 3. Authoritative Inputs

- `docs/governance/quality-gates.md`, `docs/governance/review-and-approval.md`, `docs/governance/versioning-and-status.md`, `docs/governance/catalog/artifact-applicability-matrix.yaml`, and target `capability.yaml`.

## 4. Preconditions

1. Affected Plane/Domain/Capability artifacts saved on disk and `capability.yaml` `risk_tier`/`risk_signals` declared.

## 5. Execution Procedure

1. Verify every `REQUIRED` artifact mandated by `artifact-applicability-matrix.yaml` for the capability's `risk_tier` and active `risk_signals` is present and valid.
2. Verify any `NOT_APPLICABLE_WITH_REASON` waiver includes a concrete `not_applicable_reason`.
3. Audit `APPROVED` candidates for zero `TBD`/`TODO`/`FIXME`/`[TO BE COMPLETED]`, valid `change_metadata`, matching `revision_history`, and accurate decoupled `implementation_status`.
4. Confirm zero speculative requirements or security whitewashing, then run `python scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- Gate audit findings, updated `capability.yaml` `open_questions`/`blockers` (if gaps found), and PR review readiness verdict.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/docs/ -v
```

## 8. Failure Handling

- Reject transition to `APPROVED` if `validate_docs.py` exits non-zero or unresolved `[OPEN]` / `TBD` items exist in normative sections.

## 9. Restrictions

- Never self-approve speculative requirements or security acceptances; never bypass `docs/governance/review-and-approval.md`.

## 10. Related Skills

- `traceability-audit`, `documentation-validation`, `documentation-creation`
