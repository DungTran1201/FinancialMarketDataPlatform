---
doc_id: CAP-APP-CAT-UC-001
title: "Use Case UC-CAT-001: Manage Monitored Instruments Registry"
doc_type: specification
plane: application-plane
scope_level: use-case
domain: market-experience-and-catalog
capability_id: CAP-APP-CAT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/catalog/presentation/router.py"
    - "frontend/src/modules/data-management/DataManagementModule.ts"
related_docs:
  - CAP-APP-CAT-REQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented monitored instrument listing and upsert flow plus symbol-only dict collision caveat."
---

# Use Case UC-CAT-001: Manage Monitored Instruments Registry

## 1. Actors & Preconditions

- **Actor**: Operator via `#/data-management` or `PUT /api/v1/catalog/instruments/{symbol}`.
- **Security Reality**: Target requires `catalog:write` (`operator` or `admin`); `AS-IS` executes unauthenticated.

## 2. Flow

1. Operator queries `GET /api/v1/catalog/instruments` -> receives `{provider, symbol, enabled_streams, is_active}` array.
2. Operator submits `PUT /api/v1/catalog/instruments/{symbol}` with `{provider, enabled_streams, is_active}`.
3. Backend constructs `MonitoredInstrumentConfig` and writes `runtime.monitored_instruments[symbol.upper()]`.
4. **Known Limitation**: Ephemeral dict overwrites any existing provider for the same symbol and resets on restart (`01_schema.sql` unwired).
