# Bidirectional Traceability & Impact Analysis Rule (`RULE-005`)

| Metadata | Value |
|---|---|
| **Rule ID** | `RULE-005` |
| **Rule Slug** | `traceability` |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Enforces bidirectional traceability across `BR -> FR/NFR/SEC -> RULE/UC -> Design/Contract -> Implementation -> TS/TC -> Verification Evidence` in capability `quality/traceability.yaml` and requires 6-step impact analysis before modifications.

## 2. Mandatory Directives

1. **Impact Analysis Before Editing**: Execute the 6-step impact analysis procedure in `docs/governance/traceability-and-impact-analysis.md` across `capability.yaml` (`depends_on`), contracts, code, and tests before modifying any spec or contract.
2. **Traceability Schema Conformance**: Keep `<capability>/quality/traceability.yaml` synchronized with `docs/governance/schemas/traceability.schema.json`, ensuring all referenced `design_doc_ids`, `contract_paths`, `implementation_paths`, and `test_paths` exist on disk.
3. **Honest Verification Evidence**: Record real test execution results or explicit `BLOCKED` / `NOT_IMPLEMENTED` status in `verification_evidence`.

## 3. Prohibited Actions

- Never fabricate test paths, `TC-*` IDs, or passing verification evidence for unexecuted checks.
- Never leave orphan requirement IDs or un-synced contract breaking changes across dependent capabilities.

## 4. Verification Mechanism

- `scripts/docs/validate_docs.py` (`VAL-TRAC-SCHEMA-001`, `VAL-TRAC-001`, `VAL-LINK-001`).
