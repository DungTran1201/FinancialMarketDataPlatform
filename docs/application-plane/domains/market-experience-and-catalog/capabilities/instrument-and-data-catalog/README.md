---
doc_id: CAP-APP-CAT-DOC-001
title: "Capability: Instrument & Data Catalog (CAP-APP-CAT-001)"
doc_type: index
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
    - "deploy/postgres/init/01_schema.sql"
related_docs:
  - APP-DOM-MKT-001
  - CAP-APP-CAT-REQ-001
  - CAP-APP-CAT-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Indexed all artifacts for CAP-APP-CAT-001."
---

# Capability: Instrument & Data Catalog (`CAP-APP-CAT-001`)

## 1. Requirements, Use Cases, Design & Data

- [capability.yaml](capability.yaml) (`MEDIUM` with `schema_or_db_migration: true` & `cross_plane_dependencies: true`)
- [requirements/capability-specification.md](requirements/capability-specification.md) (`CAP-APP-CAT-REQ-001`)
- [requirements/nfr.md](requirements/nfr.md) (`CAP-APP-CAT-NFR-001`)
- [use-cases/uc-cat-001-manage-monitored-instruments.md](use-cases/uc-cat-001-manage-monitored-instruments.md) (`UC-CAT-001`)
- [use-cases/uc-cat-002-inspect-freshness-lineage-and-pipeline.md](use-cases/uc-cat-002-inspect-freshness-lineage-and-pipeline.md) (`UC-CAT-002`)
- [design/component-design.md](design/component-design.md) (`CAP-APP-CAT-COMP-001`)
- [contracts/openapi.yaml](contracts/openapi.yaml), [contracts/error-catalog.md](contracts/error-catalog.md)
- [data/data-model.md](data/data-model.md), [data/database-design.md](data/database-design.md), [data/catalog-erd.md](data/catalog-erd.md)
- [quality/test-scenarios.md](quality/test-scenarios.md), [quality/test-cases.yaml](quality/test-cases.yaml), [quality/traceability.yaml](quality/traceability.yaml)
- Plane C4 & Ops: [application-c4-container.md](../../../../architecture/diagrams/application-c4-container.md), [runbook.md](../../../../operations/runbook.md), [incident-and-recovery.md](../../../../operations/incident-and-recovery.md), [test-plan.md](../../../../operations/test-plan.md)
