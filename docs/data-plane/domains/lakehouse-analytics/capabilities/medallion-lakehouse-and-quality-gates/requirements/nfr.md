---
doc_id: CAP-DP-LAK-NFR-001
title: "Non-Functional Requirements: Lakehouse Atomicity & Retention"
doc_type: specification
plane: data-plane
scope_level: capability
domain: lakehouse-analytics
capability_id: CAP-DP-LAK-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/lakehouse/silver/merge_engine.py"
    - "deploy/iceberg/catalog-config.yaml"
related_docs:
  - CAP-DP-LAK-SPEC-001
requirement_ids:
  - NFR-LAK-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented atomic Parquet write mechanics and snapshot retention discrepancy."
---

# Non-Functional Requirements: Lakehouse Atomicity & Retention

## 1. File Atomicity & Snapshot Policies `[REQUIRED]`

| NFR ID | Attribute | `AS-IS` Mechanism | Open Target Gap |
|---|---|---|---|
| `NFR-LAK-001` | Crash-Safe File Replacement & Compaction | Atomic `.tmp` writes + `replace()` across Bronze/Silver/Gold; Silver wraps Parquet IO + compaction unlink in `RLock`. | Metadata JSON writes (`L358-364`) lack `_IO_LOCK`; target file size (`128 MiB`) and snapshot count (`5` vs `10`) are un-reconciled (`OPEN-LAK-001`). |

## 2. Batch Latency & Storage Sizing Disclosure

End-to-end medallion compaction SLA and multi-terabyte storage retention targets are unapproved (`OPEN`).
