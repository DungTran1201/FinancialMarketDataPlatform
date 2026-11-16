---
doc_id: TPL-DIAG-BPMN-001
title: "Template: BPMN 2.0.2 Swimlane Workflow Diagram"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: business-analyst
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/diagrams/bpmn-diagram.template.md"
related_docs:
  - GOV-STD-DIAG-001
  - GOV-STD-REQ-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created BPMN 2.0.2 swimlane workflow diagram template with optional XML sidecar reference."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial V2 BPMN diagram template."
---

# Template: BPMN 2.0.2 Swimlane Workflow Diagram

Use for multi-actor business or operational workflows with explicit swimlane handoffs, exclusive/parallel gateways, error boundaries, or SLA timers derived from a Workflow Specification. When instantiated, set `doc_type: diagram` and `source_of_truth.is_authoritative: false`.

---

# Diagram: `<Workflow Name> (Swimlane Workflow)`

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-<SCOPE>-NNN` |
| **Title & Purpose** | `<Title — One-sentence workflow scope>` |
| **Owner Role & Scope** | `<owner-role> / <capability>` |
| **Authoritative Source** | `[<Workflow Spec Title>](<relative/path/to/workflow.md>)` (`<DOC-ID>`) |
| **Notation** | `Mermaid Swimlane-style Flowchart (flowchart TB; non-BPMN 2.0.2)` *or* `Formal BPMN 2.0.2 XML` (`<workflow>.bpmn`) |
| **Version & Status** | `<X.Y.Z> — <DRAFT|IN_REVIEW|APPROVED|DEPRECATED>` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    subgraph lane_initiator["Swimlane: <Initiator Actor / Upstream Trigger>"]
        ev_start(("Start Event: <Trigger>"))
        task_submit["Task: <Submit / Emit Request>"]
    end

    subgraph lane_processor["Swimlane: <Processor / Service>"]
        task_validate["Task: <Validate Input & Rule CHECK>"]
        gw_valid{"Gateway: <Valid?>"}
        task_execute["Task: <Execute Core Action>"]
        ev_end_ok(("End Event: <Completed>"))
        ev_end_err(("End Event: <Rejected / DLQ>"))
    end

    ev_start -->|"Trigger Payload"| task_submit
    task_submit -->|"Submit Message / Call"| task_validate
    task_validate -->|"Outcome"| gw_valid
    gw_valid -->|"Yes [RULE-DOM-001]"| task_execute
    gw_valid -->|"No [Validation Error]"| ev_end_err
    task_execute -->|"Acknowledge"| ev_end_ok
```

## 3. Legend `[REQUIRED]`

- **Circle (`((...))`)**: Start, intermediate, or terminating BPMN event.
- **Rectangle (`[...]`)**: Atomic task or activity owned by the enclosing swimlane.
- **Diamond (`{...}`)**: Decision or branching gateway referencing governing `RULE-...` IDs.
- **Subgraph**: Actor or system swimlane representing ownership handoff.

## 4. BPMN 2.0 XML Companion Reference `[OPTIONAL]`

- Attach a validated `.bpmn` XML path only if executable workflow modeling is required and validated against BPMN 2.0.2 XSD.
