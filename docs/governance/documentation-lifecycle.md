---
doc_id: GOV-POL-LIFE-001
title: "Documentation Lifecycle Policy"
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
    - "docs/governance/documentation-lifecycle.md"
related_docs:
  - GOV-POL-VER-001
  - GOV-POL-CHG-001
  - GOV-POL-GATE-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Defined the 9-stage documentation lifecycle and decoupled Document Status from Implementation Status."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Initial Documentation V2 lifecycle specification."
---

# Documentation Lifecycle Policy

## 1. Nine-Stage Lifecycle

Every capability or platform change MUST progress explicitly through these nine lifecycle stages:

| Stage | Objective | Primary Owner | Exit Gate / Evidence |
|---|---|---|---|
| **1. Discovery and Scope** | Audit `AS-IS` state, define capability boundaries, dependencies, risk tier, and open questions | `business-analyst` / `system-architect` | `capability.yaml` initialized + [definition-of-ready.md](definition-of-ready.md) |
| **2. Requirements Analysis** | Author atomic `BR`/`FR`/`NFR`/`RULE` artifacts and verify no silent assumptions | `business-analyst` | Requirements pass [requirements-standards.md](standards/requirements-standards.md) |
| **3. Specification** | Define Use Cases, Acceptance Criteria, Security Requirements, Data Models & Contracts | Domain/Capability Owners | Applicable artifacts per [artifact-applicability-matrix.yaml](catalog/artifact-applicability-matrix.yaml) |
| **4. Architecture and Design** | Produce scoped component design, ADRs, threat model, database design, and diagrams | `system-architect` / `data-architect` / `security-architect` / `ai-engineer` | Design artifacts linked to requirements |
| **5. Review and Approval** | Execute peer, architecture, security, and QA reviews; obtain human approval | `accountable_role` per [roles-and-raci.md](roles-and-raci.md) | `status: APPROVED` + `change_metadata` populated |
| **6. Implementation** | Build application/data/infra code strictly against `APPROVED` contracts and designs | `fullstack-engineer` / `data-architect` / `database-architect` / `ai-engineer` | `implementation_status` updated (`PARTIALLY_IMPLEMENTED` -> `IMPLEMENTED`) |
| **7. Verification** | Execute unit, contract, integration, security, and operational tests; capture evidence | `qa-lead` / `security-architect` | Test evidence recorded -> `implementation_status: VERIFIED` |
| **8. Release and Operations** | Finalize deployment descriptors, SLO monitoring, and SRE runbooks | `devops-sre` | [definition-of-done.md](definition-of-done.md) satisfied |
| **9. Change and Deprecation** | Execute impact analysis for revisions, deprecate superseded artifacts, or retire obsolete scopes | `documentation-architect` | `DEPRECATED` + `superseded_by` recorded per [change-management.md](change-management.md) |

## 2. Strict Separation of Document Status and Implementation Status

Document approval and implementation verification are independent dimensions and MUST NEVER be collapsed into one flag:

- **Document Status (`status`)**: `DRAFT` -> `IN_REVIEW` -> `APPROVED` -> `DEPRECATED` (tracks specification readiness and sign-off).
- **Implementation Status (`implementation_status`)**: `PLANNED` -> `NOT_IMPLEMENTED` -> `SIMULATED` -> `PARTIALLY_IMPLEMENTED` -> `IMPLEMENTED` -> `VERIFIED` (tracks software/runtime reality).

**Mandatory Invariant**: Setting `status: APPROVED` on a specification MUST NOT imply `implementation_status: IMPLEMENTED` or `VERIFIED`. Conversely, existing code MUST NOT be described as `status: APPROVED` if it violates security or architectural baselines without review.
