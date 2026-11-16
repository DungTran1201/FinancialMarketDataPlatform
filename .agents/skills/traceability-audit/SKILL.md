---
name: traceability-audit
description: Audits bidirectional traceability across capability traceability.yaml and docs/governance/schemas/.
---

# Skill: Bidirectional Traceability Audit (`SKILL-015`)

## 1. Description

Verifies end-to-end 8-link bidirectional traceability (`BR -> FR/NFR/SEC -> RULE/UC -> Design -> Contract -> Implementation -> TS/TC -> Verification Evidence`) in `<capability>/quality/traceability.yaml` and cross-capability `depends_on` references.

## 2. Trigger Conditions

- Impact analysis prior to specification edits, Stage 5/7 audits, or after modifying IDs, contracts, code paths, or test paths (`documentation-auditor`, `qa-reviewer`, `business-analyst`).

## 3. Authoritative Inputs

- `docs/governance/traceability-and-impact-analysis.md`, `docs/governance/schemas/traceability.schema.json`, `<capability>/capability.yaml`, `<capability>/quality/traceability.yaml`, and `scripts/docs/validate_docs.py`.

## 4. Preconditions

1. Target capability `capability.yaml` and `quality/traceability.yaml` exist and parse as valid YAML.

## 5. Execution Procedure

1. Run `python scripts/docs/validate_docs.py` to verify `traceability.schema.json` conformance, `design_doc_ids`, `contract_paths`, `implementation_paths`, and `test_paths`.
2. Inspect forward linkage (`BR -> FR/NFR/SEC -> UC/RULE -> Design/Contract -> TC`) and backward linkage (`Implementation/Test -> FR/SEC`) for orphans.
3. Verify `verification_evidence` reflects real executed tests or explicit `BLOCKED` status.
4. Re-run `python scripts/docs/validate_docs.py` and `python -m pytest tests/docs/ -v`.

## 6. Output Artifacts

- Synchronized `<capability>/quality/traceability.yaml` and zero-error `VAL-TRAC-001` / `VAL-TRAC-SCHEMA-001` validation output.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/docs/ -v
```

## 8. Failure Handling

- Fix orphan IDs or broken file/doc_id references in `traceability.yaml` before completing the task.

## 9. Restrictions

- Never fabricate `TC-*` IDs or `verification_evidence` without real tests; never renumber existing IDs.

## 10. Related Skills

- `requirements-engineering`, `test-modeling`, `documentation-validation`
