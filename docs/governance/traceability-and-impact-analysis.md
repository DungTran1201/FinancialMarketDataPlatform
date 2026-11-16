---
doc_id: GOV-POL-TRAC-001
title: "Bidirectional Traceability & Change Impact Analysis Standard"
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
    - "docs/governance/traceability-and-impact-analysis.md"
related_docs:
  - GOV-STD-REQ-001
  - GOV-POL-CHG-001
  - GOV-STD-QA-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Defined end-to-end 8-link traceability chain and mandatory 6-step change impact analysis procedure."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial Documentation V2 traceability and impact analysis standard."
---

# Bidirectional Traceability & Change Impact Analysis Standard

## 1. End-to-End Traceability Chain

Every Phase 2 capability (per [artifact-applicability-matrix.yaml](catalog/artifact-applicability-matrix.yaml)) MUST maintain machine-readable bidirectional traceability in `traceability.yaml` ([traceability.template.yaml](templates/quality/traceability.template.yaml), validated against [traceability.schema.json](schemas/traceability.schema.json)) across the following chain:

`Product / Business Need (BR)` -> `Requirement (FR / NFR / SEC)` -> `Business Rule / Use Case (RULE / UC)` -> `Design (Component / ADR / Diagram)` -> `Contract / Data Model (OpenAPI / AsyncAPI / Data Contract / Schema)` -> `Implementation (Code / DDL / Config Paths)` -> `Test (TS / TC)` -> `Verification Evidence (Test Report / Command Output)`

- **Forward Traceability**: Ensures every business need and requirement is designed, implemented, and tested (no orphan requirements).
- **Backward Traceability**: Ensures every contract, DB schema, implementation module, and test case exists for an approved need (no scope creep or dead artifacts).

## 2. Mandatory Change Impact Analysis Procedure

Before editing any existing specification, contract, schema, or design artifact, the author or AI Agent MUST execute these six steps:

1. **Identify Seed Artifact & IDs**: Record the target `doc_id`, requirement IDs (`FR`/`NFR`/`RULE`), contract operations/topics, or entities being modified.
2. **Traverse Downstream Links**: Inspect `traceability.yaml` and `docs-index.yaml` to identify all dependent Use Cases, Component Designs, OpenAPI/AsyncAPI contracts, DB designs, Security threat scenarios/authz rules, Test Cases, and Runbooks.
3. **Traverse Cross-Plane & Cross-Capability Dependencies**: Inspect `depends_on` across sibling `capability.yaml` manifests (for example, changes to a Data Plane event contract impacting Application Plane queries or Intelligence Plane tools).
4. **Inspect Code & Test Blast Radius**: Locate exact `src/`, `frontend/`, `deploy/`, and `tests/` paths mapped in `traceability.yaml`.
5. **Classify Breaking vs. Non-Breaking Impact**:
   - **Non-Breaking**: Additive optional fields, clarifications, new non-conflicting capabilities.
   - **Breaking**: Removed/renamed fields, auth policy tightening, changed natural keys, changed latency/availability commitments (requires version bump, migration/deprecation plan, and higher review tier).
6. **Synchronize Atomically**: Update impacted specifications, contracts, traceability links, and verification plans together in the same pull request, or log explicit `OPEN` / `BLOCKED` blockers for deferred consumer updates.
