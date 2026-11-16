---
doc_id: DIAG-INT-ORC-PROV-001
title: "Evidence & Provenance Flow Diagram"
doc_type: diagram
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/architecture/evaluation-and-observability.md"
    - "src/intelligence/reporting/validator.py"
related_docs:
  - INT-ARCH-EVAL-001
  - CAP-INT-ORC-UC-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created Evidence & Provenance Flow Diagram illustrating UUIDv4 invocation_id tracking and validation."
---

# Evidence & Provenance Flow Diagram

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-ORC-PROV-001` |
| **Purpose** | Trace how `invocation_id` provenance flows from `ControlledToolGateway` through `evidence_trail` to `ReportValidator`. |
| **Scope & Owner** | `capability` (`CAP-INT-ORC-001`) / `ai-engineer` |
| **Authoritative Source** | [evaluation-and-observability.md](../../../../../architecture/evaluation-and-observability.md) (`INT-ARCH-EVAL-001`) |
| **Notation** | Mermaid `flowchart LR` (Data / Provenance Flow) |
| **Version & Status** | `2.0.0` / `DRAFT` (`PARTIALLY_IMPLEMENTED`) |

```mermaid
flowchart LR
    GW["ControlledToolGateway"] -->|"Generates UUIDv4 invocation_id"| ENV["ToolExecutionEnvelope (data + ToolProvenanceMetadata)"]
    ENV -->|"Appended in Node 3"| TRAIL["AgentWorkflowState.evidence_trail"]
    ENV -->|"Appended"| AUDIT["gateway._audit_log (In-Memory AS-IS)"]
    TRAIL -->|"Read by synthesize_narrative()"| REP["report dict (quantitative_evidence + provenance_citations)"]
    TRAIL -->|"valid_ids set"| VAL["ReportValidator.validate_report()"]
    REP -->|"Check non-empty & id in valid_ids"| VAL
    VAL -->|"Pass"| PERSIST["generate_analysis_report -> runtime.reports[run_id]"]
    VAL -->|"Missing or fabricated id"| ERR["raise ReportProvenanceError"]
```

**Legend**: Solid arrows (`-->`) trace `AS-IS` provenance metadata propagation and verification.
