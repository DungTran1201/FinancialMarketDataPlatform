---
doc_id: GOV-POL-DOD-001
title: "Documentation & Verification Definition of Done (DoD)"
doc_type: governance
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: qa-lead
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/definition-of-done.md"
related_docs:
  - GOV-POL-DOR-001
  - GOV-POL-GATE-001
  - GOV-STD-QA-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Defined Documentation and Verification Definition of Done distinguishing document approval from verified code."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Initial Documentation V2 Definition of Done."
---

# Documentation & Verification Definition of Done (DoD)

## 1. Documentation Change DoD

A documentation task is **Done** only when ALL of the following hold:

1. **Applicability Satisfied**: Every `REQUIRED` artifact in [artifact-applicability-matrix.yaml](catalog/artifact-applicability-matrix.yaml) for the capability's risk tier and signals exists and is meaningfully populated; every `NOT_APPLICABLE_WITH_REASON` exclusion records a concrete rationale in `capability.yaml`.
2. **Metadata & Source-of-Truth Integrity**: Valid YAML frontmatter, unique IDs, accurate `status` and `implementation_status`, and declared `source_of_truth` links.
3. **Traceability & Impact Sync**: Upstream/downstream links in `traceability.yaml` (where applicable) and impacted dependent docs are synchronized.
4. **Automated Validation Passes**: `python scripts/docs/validate_docs.py` exits `0` and all documentation validator tests pass.
5. **Review Sign-Off**: Accountable owner review completed per [review-and-approval.md](review-and-approval.md).

## 2. Feature / Implementation Verification DoD

A software capability is **Verified (`implementation_status: VERIFIED`)** only when:

1. **Documentation DoD Passed**: Specifications, contracts, and `AS-IS` documentation accurately reflect implemented behavior without overclaiming simulated components as live infrastructure.
2. **Test Exit Criteria Passed**: All `P0` / `CRITICAL` test cases in `test-cases.yaml` pass with actual execution evidence (explicitly recording in-memory vs. containerized execution environment).
3. **Security & Operational Readiness**: Required security controls (auth/authz, secrets isolation) and operational runbooks/alerts are verified for the target risk tier.
4. **No Silent Regressions**: Existing application test suites (`pytest`, `ruff`, frontend tests) pass without skipped or weakened assertions.
