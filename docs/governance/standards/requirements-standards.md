---
doc_id: GOV-STD-REQ-001
title: "Requirements Engineering Standards"
doc_type: standard
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
    - "docs/governance/standards/requirements-standards.md"
related_docs:
  - GOV-STD-REG-001
  - GOV-STD-WRIT-001
  - GOV-POL-TRAC-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established ISO/IEC/IEEE 29148-aligned rules for BR, FR, NFR, Business Rules, Use Cases, AC, constraints, assumptions, open questions, priority, and traceability."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial Documentation V2 requirements engineering standard."
---

# Requirements Engineering Standards

Aligned with **ISO/IEC/IEEE 29148:2018** (noting active 3rd Edition DIS revision in [standards-register.md](standards-register.md)).

## 1. Requirement Artifact Taxonomy

| Category | ID Pattern | Purpose | Separation Rule |
|---|---|---|---|
| **Business Requirement (BR)** | `BR-<DOM>-NNN` | Business outcome, regulatory/commercial need, and scope boundary | MUST state business value and success criteria, not UI widgets or code modules. |
| **Functional Requirement (FR)** | `FR-<DOM>-NNN` | Observable behavior the system MUST perform under defined conditions | MUST state **WHAT** the system does, separated from **HOW** (framework, DB engine, class name). |
| **Non-Functional Requirement (NFR)** | `NFR-<DOM>-NNN` | Measurable quality attribute, constraint, or operational threshold | MUST define quantifiable metric, measurement condition, and verification method (or mark target `[OPEN]`). |
| **Business Rule (RULE)** | `RULE-<DOM>-NNN` | Invariant policy, domain formula, or decision constraint constraining behavior | MUST state exact predicate/formula and violation consequence; MUST be reusable across FRs/UCs. |
| **Use Case (UC)** | `UC-<DOM>-NNN` | Actor-goal interaction covering trigger, preconditions, main flow, alternative flows, and exceptions | MUST link to parent FRs/BRs and specify postconditions for both success and failure paths. |
| **Acceptance Criteria (AC)** | `AC-<DOM>-NNN` | Objective Given/When/Then or assertion conditions verifying an FR/UC | MUST be deterministically testable without subjective adjectives ("fast", "user-friendly"). |
| **Constraint** | `CON-<DOM>-NNN` | Non-negotiable technical, legal, budget, or timeline boundary | MUST record source authority and non-negotiable impact. |

## 2. Mandatory Quality Criteria (Every Requirement)

Every BR, FR, NFR, and Business Rule MUST satisfy all eight quality properties:

1. **Atomic**: Expresses one single verifiable requirement (no compound "and/or" multi-behaviors under one ID).
2. **Unambiguous**: Only one technical interpretation exists; avoids vague qualifiers ("etc.", "appropriate", "timely", "fast").
3. **Feasible**: Technically achievable within project constraints.
4. **Necessary**: Traces upward to a validated business need or risk mitigation; speculative features MUST NOT be included.
5. **Consistent**: Does not contradict any peer requirement, business rule, or approved ADR.
6. **Verifiable**: Defines objective pass/fail verification (`Inspection`, `Analysis`, `Demonstration`, or `Test`).
7. **Traceable**: Assigned a stable ID linked upstream to Need/BR and downstream to Design, Contract, Implementation, and Test Cases.
8. **Scoped**: Bound to a single Plane/Domain/Capability owner (cross-plane requirements MUST be split into plane-owned contracts).

## 3. Priority, Dependencies, Assumptions & Unresolved Decisions

1. **Priority Scale**: Every requirement MUST declare one MoSCoW/risk priority: `MUST_HAVE (P0)`, `SHOULD_HAVE (P1)`, `COULD_HAVE (P2)`, or `WONT_HAVE_NOW (P3)`.
2. **Dependencies**: Cross-capability requirements MUST record `depends_on` (`CAP-...` or `FR-...`) in both the requirement table and `capability.yaml`.
3. **Assumptions**: Working assumptions MUST carry an `ASSUMP-...` ID, explicit `[ASSUMPTION]` tag, owner, and validation deadline.
4. **Open Questions & Missing Decisions**:
   - Any missing business decision, unconfirmed metric threshold, or unresolved policy MUST be logged explicitly as `OPEN`, `NEEDS_CLARIFICATION`, or `BLOCKED` in the capability's Open Questions register and `capability.yaml`.
   - Agents MUST NOT silently promote an assumption or infer an unconfirmed threshold into an `APPROVED` requirement.
5. **Verification & Traceability**: An FR/NFR MUST NOT be marked verified unless linked `TC-...` test cases and execution evidence exist per [qa-and-testing-standards.md](qa-and-testing-standards.md).
