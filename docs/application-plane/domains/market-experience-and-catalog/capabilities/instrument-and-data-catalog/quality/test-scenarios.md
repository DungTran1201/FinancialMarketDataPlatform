---
doc_id: CAP-APP-CAT-TS-001
title: "Test Scenarios: Instrument & Data Catalog"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-CAT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: qa-lead
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/integration/test_three_planes_framework.py"
related_docs:
  - CAP-APP-CAT-DOC-001
  - CAP-APP-CAT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Documented catalog API verification scenarios and Postgres persistence gap."
---

# Test Scenarios: Instrument & Data Catalog

## 1. Covered `AS-IS` Scenarios

- **`TS-CAT-001`**: List default instruments -> `PUT /catalog/instruments/ADAUSDT` -> verify inclusion and freshness report shape (`GET /catalog/freshness`).
- **`TS-CAT-002`**: Trigger `POST /catalog/lakehouse/pipeline` -> confirm Bronze/Silver/DQ counts returned.

## 2. Unverified Gaps

- Postgres `monitored_instruments` persistence across restarts and multi-provider key collisions remain unimplemented (`NOT_IMPLEMENTED`).
- Frontend `DataManagementModule.ts` lineage display without mock fallback is unverified in this workspace.
