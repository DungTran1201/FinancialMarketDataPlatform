---
doc_id: CAP-APP-MKT-DOC-001
title: "Capability: Market & Analytics Query Portal (CAP-APP-MKT-001)"
doc_type: index
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-MKT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: business-analyst
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/market/presentation/router.py"
    - "src/serving/api/modules/historical/presentation/router.py"
    - "src/serving/api/modules/analytics/presentation/router.py"
    - "frontend/src/modules/market-analytics/MarketAnalyticsModule.ts"
related_docs:
  - APP-DOM-MKT-001
  - CAP-APP-MKT-REQ-001
  - CAP-APP-MKT-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Indexed all artifacts for CAP-APP-MKT-001."
---

# Capability: Market & Analytics Query Portal (`CAP-APP-MKT-001`)

## 1. Requirements, Use Cases & Workflows

- [capability.yaml](capability.yaml) (`MEDIUM`)
- [requirements/capability-specification.md](requirements/capability-specification.md) (`CAP-APP-MKT-REQ-001`)
- [requirements/business-rules.md](requirements/business-rules.md) (`CAP-APP-MKT-RULE-001`)
- [requirements/nfr.md](requirements/nfr.md) (`CAP-APP-MKT-NFR-001`)
- [use-cases/uc-mkt-001-query-hot-market-and-orderbook.md](use-cases/uc-mkt-001-query-hot-market-and-orderbook.md) (`UC-MKT-001`)
- [use-cases/uc-mkt-002-query-klines-trades-and-backfill.md](use-cases/uc-mkt-002-query-klines-trades-and-backfill.md) (`UC-MKT-002`)
- [use-cases/uc-mkt-003-analytics-correlations-and-anomalies.md](use-cases/uc-mkt-003-analytics-correlations-and-anomalies.md) (`UC-MKT-003`)
- [workflows/hot-to-olap-fallback-sequence.md](workflows/hot-to-olap-fallback-sequence.md) (`DIAG-APP-MKT-SEQ-001`)
- [workflows/backfill-job-state-machine.md](workflows/backfill-job-state-machine.md) (`DIAG-APP-MKT-STATE-001`)

## 2. Design, Contracts, Quality & Plane References

- [design/component-design.md](design/component-design.md) (`CAP-APP-MKT-COMP-001`)
- [contracts/openapi.yaml](contracts/openapi.yaml), [contracts/error-catalog.md](contracts/error-catalog.md), [contracts/data-contract.yaml](contracts/data-contract.yaml)
- [quality/test-scenarios.md](quality/test-scenarios.md), [quality/test-cases.yaml](quality/test-cases.yaml), [quality/traceability.yaml](quality/traceability.yaml)
- Plane C4 & Ops: [application-c4-container.md](../../../../architecture/diagrams/application-c4-container.md), [runbook.md](../../../../operations/runbook.md), [test-plan.md](../../../../operations/test-plan.md)
