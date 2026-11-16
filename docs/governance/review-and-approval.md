---
doc_id: GOV-POL-REV-001
title: "Documentation Review & Approval Policy"
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
    - "docs/governance/review-and-approval.md"
related_docs:
  - GOV-POL-RACI-001
  - GOV-POL-VER-001
  - GOV-POL-GATE-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established risk-tiered review workflows, explicit human approval mandates, and change metadata requirements."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Initial Documentation V2 review and approval policy."
---

# Documentation Review & Approval Policy

## 1. Risk-Tiered Review Requirements

Every capability or structural documentation change MUST undergo review proportional to its risk tier in [artifact-applicability-matrix.yaml](catalog/artifact-applicability-matrix.yaml):

| Risk Tier | Required Reviewers | Approval Authority |
|---|---|---|
| `LOW` | Peer engineer + automated `validate_docs.py` | Domain / Capability `accountable_role` |
| `MEDIUM` | `business-analyst` + `system-architect` / `data-architect` + `qa-lead` | Owning `accountable_role` + PR review |
| `HIGH_CRITICAL` | All `MEDIUM` reviewers + `security-architect` + `devops-sre` (+ `ai-engineer` for Intelligence Plane) | Human repository owner + domain `accountable_role` |

## 2. Preconditions for Transitioning `IN_REVIEW` -> `APPROVED`

A document MUST NOT transition to `status: APPROVED` unless all of the following hold:

1. Automated validation (`scripts/docs/validate_docs.py`) exits with code `0`.
2. Zero `[TO BE COMPLETED]`, `TBD`, or `TODO` markers remain in normative specification sections.
3. Any unresolved external choices are explicitly documented in `open_questions` (or the specification itself does not pretend an unapproved assumption is settled).
4. Frontmatter `change_metadata` records `approved_by`, `approved_at`, and `change_summary`, and `revision_history` includes a matching `version` record.
5. An AI Agent MUST NOT self-approve speculative business requirements, security risk acceptances, or architectural decisions on behalf of human owners.

## 3. Pull-Request Delivery

All non-trivial documentation changes SHOULD be submitted via dedicated branches and reviewable pull requests containing:

- Scope summary (Plane / Domain / Capability).
- Impact analysis results ([traceability-and-impact-analysis.md](traceability-and-impact-analysis.md)).
- Validator execution output (`scripts/docs/validate_docs.py`).
