---
doc_id: TPL-DIAG-DFD-001
title: "Template: Data Flow & Lineage Diagram (DFD)"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/diagrams/data-flow-diagram.template.md"
related_docs:
  - GOV-STD-DIAG-001
  - GOV-STD-DATA-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Data Flow & Lineage Diagram template for ingestion, streaming, medallion, and serving pipelines."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Initial V2 Data Flow diagram template."
---

# Template: Data Flow & Lineage Diagram (DFD)

Use for pipelines, broker fan-out, medallion stage transformations, quality gates, dead-letter routing, and serving sink paths. Derived strictly from Data Architecture and Data Contract specs. When instantiated, set `doc_type: diagram` and `source_of_truth.is_authoritative: false`.

---

# Diagram: `<Pipeline / Domain Name> Data Flow`

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-<SCOPE>-NNN` |
| **Title & Purpose** | `<Title — One-sentence data lineage scope>` |
| **Owner Role & Scope** | `data-architect / <plane|capability>` |
| **Authoritative Source** | `[<Data Architecture / Data Model>](<relative/path/to/source.md>)` (`<DOC-ID>`) |
| **Notation** | `Mermaid flowchart LR` (`DFD`) |
| **Version & Status** | `<X.Y.Z> — <DRAFT|IN_REVIEW|APPROVED|DEPRECATED>` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart LR
    src_ext["<External Source>"]
    proc_ingest["<Ingest & Normalize Process>"]
    bus_stream["<Event Topic / Channel>"]
    gate_dq{"<Data Quality Gate>"}
    store_dlq[("<Dead-Letter Topic / Quarantine>")]
    store_target[("<Target Lakehouse / Serving Store>")]

    src_ext -->|"Raw Payload (Protocol)"| proc_ingest
    proc_ingest -->|"Envelope v1 (Decimal)"| bus_stream
    bus_stream -->|"Stream Consume"| gate_dq
    gate_dq -->|"Pass Schema & Rules"| store_target
    gate_dq -.->|"Fail Validation / Schema Error"| store_dlq
```

## 3. Legend `[REQUIRED]`

- **Rectangle (`[...]`)**: Active collector, stream consumer, or batch job.
- **Diamond (`{...}`)**: Schema, freshness, or financial invariant quality gate.
- **Cylinder (`[(...)]`)**: Durable event log, object store tier, or database sink.
- **Solid vs. Dashed Arrows**: Primary data lineage (`-->`) vs. quarantine/DLQ side-path (`-.->`).
