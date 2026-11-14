---
name: documentation-review
description: Audits placeholder hygiene, phase gates (G0..G6), and status promotion readiness.
---

# Skill: Documentation Quality & Gate Audit (`SKILL-014`)

## 1. Description

Audits documentation completeness, placeholder hygiene, and phase gate (`G0_DISCOVERY`..`G6_RELEASE`) compliance before status promotion.

## 2. Trigger Conditions

- Phase `14-governance` or Work Item `review.md` gate sign-off (`documentation-auditor`).

## 3. Authoritative Inputs

- `work-items/<ID>/artifact-plan.yaml`, `review.md`, `.agents/config/phase-gates.yaml`, `status-lifecycle.yaml`, `docs/product/14-governance/`.

## 4. Preconditions

1. Target `README.md` read; all planned artifacts in `work-items/<ID>/artifact-plan.yaml` authored.

## 5. Execution Procedure

1. Verify every required artifact in `artifact-plan.yaml` exists and conforms to its `docs/templates/` structure.
2. Scan for forbidden `[TO BE COMPLETED]` placeholders or untagged assumptions in `APPROVED`/`BASELINED` documents.
3. Verify phase gate exit criteria in `.agents/config/phase-gates.yaml` and record findings in `work-items/<ID>/review.md`.
4. Run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `work-items/<ID>/review.md` and `docs/product/14-governance/*.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Reject promotion to `APPROVED` or `BASELINED` if any validator fails or any `[OPEN QUESTION]` remains unresolved.

## 9. Restrictions

- Never self-approve speculative requirements; never bypass `.agents/config/status-lifecycle.yaml`.

## 10. Related Skills

- `traceability-audit`, `documentation-validation`, `documentation-creation`
