---
doc_id: GOV-POL-DOR-001
title: "Documentation & Implementation Definition of Ready (DoR)"
doc_type: governance
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: business-analyst
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/definition-of-ready.md"
related_docs:
  - GOV-POL-LIFE-001
  - GOV-POL-DOD-001
  - GOV-CAT-MAT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Defined Definition of Ready criteria for starting Phase 2 documentation and implementation work."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial Documentation V2 Definition of Ready."
---

# Documentation & Implementation Definition of Ready (DoR)

## 1. DoR for Starting Specification Work on a Capability

Before authoring detailed Phase 2 specifications for a capability, all of the following MUST be satisfied:

1. **Owning Plane & Domain Resolved**: The capability is registered in its Plane and Domain `README.md`.
2. **Manifest Initialized**: `capability.yaml` exists with valid `capability_id`, `plane`, `domain`, `scope`, `in_scope`, `out_of_scope`, and `owner_role`.
3. **Risk Tier Assessed**: `risk_tier` (`LOW | MEDIUM | HIGH_CRITICAL`) and applicability flags are populated in `capability.yaml`.
4. **AS-IS Baseline Inspected**: Relevant existing code (`src/`, `frontend/`), DDL (`deploy/`), and tests (`tests/`) have been inspected if modifying an existing subsystem.
5. **Dependencies Identified**: Upstream capabilities or shared contracts are listed in `capability.yaml`.

## 2. DoR for Starting Software Implementation

Before implementing or modifying production code (`src/`, `frontend/`, `deploy/`) for a capability:

1. **Requirements Approved**: Relevant `FR`/`NFR`/`RULE`/`AC` items are in `status: APPROVED` with zero unresolved `BLOCKED` questions on the target slice.
2. **Contracts Defined**: Required `openapi.yaml`, `asyncapi.yaml`, or `data-contract.yaml` schemas exist and pass structural validation.
3. **Security & Data Gates Cleared**: For `HIGH_CRITICAL` or auth/data/agent capabilities, the Threat Model, Authorization Matrix, and Migration/Rollback design are `IN_REVIEW` or `APPROVED`.
4. **Acceptance Criteria Testable**: Every scoped `FR`/`NFR` maps to clear acceptance criteria (`AC-...`) or test scenarios (`TS-...`).
