---
doc_id: CAP-APP-CAT-COMP-001
title: "Component & Screen Design: Catalog Router & DataManagementModule"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-CAT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/catalog/presentation/router.py"
    - "frontend/src/modules/data-management/DataManagementModule.ts"
    - "frontend/src/services/api/catalog.service.ts"
related_docs:
  - CAP-APP-CAT-REQ-001
  - APP-ARCH-COMPAT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Documented catalog FastAPI endpoints and DataManagementModule UI subviews and lineage mock gap."
---

# Component & Screen Design: Catalog Router & DataManagementModule

## 1. Backend Module (`src/serving/api/modules/catalog/presentation/router.py`)

- Mounts `/instruments` (`GET`), `/instruments/{symbol}` (`PUT`), `/freshness` (`GET`), `/lakehouse/pipeline` (`POST`).
- Reads `runtime.monitored_instruments` dict (`MonitoredInstrumentConfig`) and delegates lakehouse triggers through `runtime.bronze_archiver`, `runtime.silver_merge_engine`, and `runtime.quality_gate_engine`.

## 2. Frontend Screen Specification: `#/data-management` (`DataManagementModule.ts`)

- **UI Sections**: Monitored Instruments table + edit/upsert form, Multi-Tier Freshness Matrix, Medallion Storage & DQ Rule Gate Explorer, Watermarks & Lineage Graph (`catalog.service.ts`), Gold Marts browser.
- **Verified Defect (`COMPAT-007`)**: When `GET /api/v1/data-platform/v01/lineage` yields empty/fails, `CatalogService.getLineage()` injects a static 8-node/4-edge array rather than displaying an empty/error state.
