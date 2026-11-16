---
doc_id: CAP-DP-ING-ROOT
title: "Capability: Exchange Realtime & Backfill Ingestion (CAP-DP-ING-001)"
doc_type: index
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/"
related_docs:
  - DP-DOM-ING-001
  - CAP-DP-ING-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Indexed CAP-DP-ING-001 capability artifacts."
---

# Capability: Exchange Realtime & Backfill Ingestion (`CAP-DP-ING-001`)

- **Manifest**: [capability.yaml](capability.yaml) (`HIGH_CRITICAL` risk tier)
- **Requirements**: [capability-specification.md](requirements/capability-specification.md), [business-rules.md](requirements/business-rules.md), [nfr.md](requirements/nfr.md)
- **Use Case & Flows**: [use-case-ingestion-and-gap-heal.md](use-cases/use-case-ingestion-and-gap-heal.md), [ingestion-sequence.md](workflows/ingestion-sequence.md)
- **Design & Contracts**: [component-design.md](design/component-design.md), [ingestion-dfd.md](design/ingestion-dfd.md), [openapi.yaml](contracts/openapi.yaml), [error-catalog.md](contracts/error-catalog.md), Plane [asyncapi.yaml](../../../../shared-contracts/asyncapi.yaml) & [data-contract.yaml](../../../../shared-contracts/data-contract.yaml)
- **Data & Security**: [data-model.md](data/data-model.md), [database-design.md](data/database-design.md), [watermark-erd.md](data/watermark-erd.md), [threat-model.md](security/threat-model.md), [security-requirements.md](security/security-requirements.md), [threat-model-diagram.md](security/threat-model-diagram.md)
- **Quality & Ops**: [test-scenarios.md](quality/test-scenarios.md), [test-cases.yaml](quality/test-cases.yaml), [traceability.yaml](quality/traceability.yaml), Plane [runbook.md](../../../../operations/runbook.md)
