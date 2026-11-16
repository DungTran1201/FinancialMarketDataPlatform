---
doc_id: CAP-DP-LAK-001-ROOT
title: "Capability: Medallion Lakehouse, Quality Gates & Lineage (CAP-DP-LAK-001)"
doc_type: index
plane: data-plane
scope_level: capability
domain: lakehouse-analytics
capability_id: CAP-DP-LAK-001
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
    - "src/lakehouse/"
related_docs:
  - DP-DOM-LAK-001
  - CAP-DP-LAK-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Indexed CAP-DP-LAK-001 medallion processing, DQ rules, Iceberg compaction JSON manifests, and Gold marts."
---

# Capability: Medallion Lakehouse, Quality Gates & Lineage (`CAP-DP-LAK-001`)

- **Manifest**: [capability.yaml](capability.yaml) (`MEDIUM` risk tier — local Parquet & custom JSON manifests)
- **Requirements**: [capability-specification.md](requirements/capability-specification.md), [business-rules.md](requirements/business-rules.md), [nfr.md](requirements/nfr.md)
- **Design & Data**: [component-design.md](design/component-design.md), [data-model.md](data/data-model.md), [database-design.md](data/database-design.md), [lakehouse-erd.md](data/lakehouse-erd.md), Shared [data-contract.yaml](../../../../shared-contracts/data-contract.yaml)
- **Quality & Ops**: [test-scenarios.md](quality/test-scenarios.md), [test-cases.yaml](quality/test-cases.yaml), [traceability.yaml](quality/traceability.yaml), Plane [runbook.md](../../../../operations/runbook.md)
