---
doc_id: CAP-APP-CAT-ERR-001
title: "Error Catalog: Instrument & Data Catalog"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-CAT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/catalog/presentation/router.py"
related_docs:
  - APP-ERR-SHARED-001
  - CAP-APP-CAT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Cataloged catalog router HTTP error behavior and silent fallback caveats."
---

# Error Catalog: Instrument & Data Catalog

## 1. Router Behavior & Gaps

- `GET/PUT /api/v1/catalog/*` define **no domain `HTTPException` 4xx handlers** (`AS-IS`): invalid payloads rely purely on FastAPI request JSON parsing (`422` missing body) or coerce values via `str(...)` / `bool(...)`.
- Edge middleware returns `400 UNTRUSTED_HOST_HEADER`, `403 WAF_THREAT_DETECTED`, or `429 RATE_LIMIT_EXCEEDED` on gateway `8000` only (`APP-ERR-SHARED-001`).

## 2. Target Error Normalization (`OPEN`)

- Validate `symbol` format (`^[A-Z0-9]{3,20}$`), `enabled_streams` enum values, and return `401`/`403` when `catalog:write` authorization is enforced.
