---
doc_id: CAP-APP-OPS-UC-003
title: "Use Case UC-OPS-003: Run 12-Stage DataPlatformV01, Administer Config & Dispatch Services"
doc_type: specification
plane: application-plane
scope_level: use-case
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/services/data_plane.py"
    - "src/serving/api/gateway/service.py"
    - "src/serving/api/modules/platform_config/presentation/router.py"
    - "frontend/src/modules/administration/AdministrationModule.ts"
related_docs:
  - CAP-APP-OPS-REQ-001
  - DIAG-APP-OPS-STATE-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented DataPlatformV01 pipeline trigger, AdministrationModule health/config checks, and microservice dispatch."
---

# Use Case UC-OPS-003: Run 12-Stage DataPlatformV01, Administer Config & Dispatch Services

## 1. Main Gateway & Administration Flows

1. **Full 12-Stage Run (`POST /api/v1/data-platform/v01/run`)**: Executes exchange discovery, backfill, Kafka publish, hot/OLAP projections, Bronze/Silver/DQ/Gold promotion, Iceberg compaction, metrics, and lineage registration; returns `EndToEndExecutionReport`.
2. **Compaction & Gold Query**: `POST /data-platform/v01/compaction` snapshots Parquet manifests; `GET /data-platform/v01/gold/{mart_name}` queries `fct_daily_market_summary`, `fct_realized_volatility`, or `fct_orderbook_liquidity` (`404` on unknown mart).
3. **Administration & Mesh Discovery (`#/administration`)**: Queries `GET /platform/config` and `GET /microservices/{topology,health}` (checks live probe on all 7 `svc-*` apps).
4. **Arbitrary Dispatch (`POST /microservices/dispatch/{service_id}`)**: Forwards caller's `method`, `path`, `params`, and `json_body` via `MicroserviceRegistry.dispatch_internal_request` (`404` on unknown `service_id`). *(Unauthenticated security risk `THR-OPS-002`.)*

## 2. Exception Flows & Target Guards

- **`404` Unknown Service / Mart**: Returned deterministically by `dispatch/{service_id}` and `gold/{mart_name}`.
- **Target Auth**: Enforce `operator`/`admin` JWT verification and strict route allowlists on `/dispatch/{service_id}`.
