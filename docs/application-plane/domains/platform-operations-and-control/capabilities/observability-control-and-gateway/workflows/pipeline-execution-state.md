---
doc_id: DIAG-APP-OPS-STATE-001
title: "State Machine Diagram: Topology Node & Event Trace Lifecycle"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: IN_REVIEW
implementation_status: IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/platform-operations-and-control/capabilities/observability-control-and-gateway/requirements/capability-specification.md"
related_docs:
  - CAP-APP-OPS-REQ-001
  - CAP-APP-OPS-UC-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Rendered stateDiagram-v2 for Data Flow DAG node status (IDLE/ACTIVE/DELAYED/FAILED/UNAVAILABLE)."
---

# State Machine Diagram: Topology Node & Event Trace Lifecycle

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-OPS-STATE-001` |
| **Title & Purpose** | 12-Node Topology Node Operational States (`runtime.py:1224-1381`) |
| **Owner Role & Scope** | `devops-sre / CAP-APP-OPS-001` |
| **Authoritative Source** | [capability-specification.md](../requirements/capability-specification.md) (`CAP-APP-OPS-REQ-001`) |
| **Notation** | `Mermaid stateDiagram-v2` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
stateDiagram-v2
    [*] --> IDLE : "Process start (0 records)"
    IDLE --> ACTIVE : "Ingestion / Sink records > 0 & lag == 0"
    ACTIVE --> DELAYED : "kafka_total_lag > 0"
    DELAYED --> ACTIVE : "Lakehouse flush commits consumer offsets"
    ACTIVE --> FAILED : "DQ gate blocked Gold promotion OR DLQ > 0 with 0 valid"
    FAILED --> ACTIVE : "Next pipeline run passes DQ gates"
```

## 3. Legend

- **Node Statuses**: Computed dynamically in `get_observability_topology()` (`ACTIVE`, `IDLE`, `DELAYED`, `FAILED`) and `UNAVAILABLE` for Kafka Brokers 2 & 3.
