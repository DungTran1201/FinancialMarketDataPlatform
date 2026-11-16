---
doc_id: GOV-POL-CHG-001
title: "Documentation Change Management Policy"
doc_type: governance
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: documentation-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/change-management.md"
related_docs:
  - GOV-POL-LIFE-001
  - GOV-POL-VER-001
  - GOV-POL-TRAC-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Defined documentation change workflow, pull-request change metadata requirements, deprecation, and retirement rules."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Initial Documentation V2 change management policy."
---

# Documentation Change Management Policy

## 1. Change Triggers

Documentation updates MUST be triggered whenever any of the following occurs:

- A new Plane, Domain, or Capability is introduced or modified in scope.
- An API endpoint, event schema, database table, or Agent tool contract changes.
- A new security threat, authorization rule, or architectural decision (`ADR`) is raised.
- Source code inspection reveals a discrepancy between `AS-IS` documentation and actual implementation.

## 2. Change Procedure

1. **Locate Scope via Discovery Chain**: Follow [ai-agent-and-discovery-standards.md](standards/ai-agent-and-discovery-standards.md) to load only the affected Plane, Domain, and Capability manifest.
2. **Determine Applicability & Risk Tier**: Check [artifact-applicability-matrix.yaml](catalog/artifact-applicability-matrix.yaml) for the capability's risk tier (`LOW`, `MEDIUM`, `HIGH_CRITICAL`) so only relevant artifacts are touched.
3. **Run Impact Analysis**: Trace affected upstream/downstream requirements, contracts, code, and tests per [traceability-and-impact-analysis.md](traceability-and-impact-analysis.md).
4. **Edit Authoritative Source First**: Update the canonical requirement, contract (`openapi.yaml`/`asyncapi.yaml`/`data-contract.yaml`), or ADR before updating derived summaries or diagrams.
5. **Update Change Metadata**: Bump `version`, set `updated_at`, and append a `revision_history` entry. If `status` becomes or stays `APPROVED`, update `change_metadata` (`approved_by`, `approved_at`, `change_summary`).
6. **Validate & Review**: Pass `scripts/docs/validate_docs.py` and obtain sign-off via pull request per [review-and-approval.md](review-and-approval.md).

## 3. Deprecation & Retirement Rules

1. **Deprecation**: When a capability, contract, or ADR is superseded, set `status: DEPRECATED`, record `superseded_by` in frontmatter, and state the sunset policy.
2. **Retirement**: Deprecated files that no longer serve active contracts SHOULD be deleted from the active `docs/` tree after updating all references; Git history remains the permanent audit log (never create a `docs/archive/` directory).
3. **Branch Protection**: Documentation changes MUST be delivered through feature/documentation branches and pull requests rather than direct commits to `main`.
