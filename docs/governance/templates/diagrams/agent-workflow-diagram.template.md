---
doc_id: TPL-DIAG-AGENT-001
title: "Template: Agent Execution Workflow & Tool-Guard Diagram"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/diagrams/agent-workflow-diagram.template.md"
related_docs:
  - GOV-STD-DIAG-001
  - GOV-STD-AGENT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Intelligence Plane agent execution graph, tool-gateway permission, and human-approval diagram template."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Initial V2 agent workflow diagram template."
---

# Template: Agent Execution Workflow & Tool-Guard Diagram

Use for Intelligence Plane orchestrators, multi-step reasoning graphs, read-only vs. write-capable tool permission checks, iteration limits, fallback paths, and human approval checkpoints. Derived from an Agent Specification (`TPL-ARCH-AGENT-001`). When instantiated, set `doc_type: diagram` and `source_of_truth.is_authoritative: false`.

---

# Diagram: `<Agent / Workflow Name> Execution Graph`

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-<SCOPE>-NNN` |
| **Title & Purpose** | `<Title — Agent node graph, tool permissions, and loop guard>` |
| **Owner Role & Scope** | `ai-engineer / intelligence-plane` |
| **Authoritative Source** | `[<Agent Specification>](<relative/path/to/agent-spec.md>)` (`<DOC-ID>`) |
| **Notation** | `Mermaid flowchart TD` (`Agent State / Tool Graph`) |
| **Version & Status** | `<X.Y.Z> — <DRAFT|IN_REVIEW|APPROVED|DEPRECATED>` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TD
    node_start(["Trigger: <User Query / Scheduled Job>"])
    node_plan["Node: <Planner / Reasoner>"]
    gw_tool{"Tool Permission & Budget Check"}
    node_read["Tool Gateway: <Read-Only Tools>"]
    gw_approval{"Human Approval Required? (Write Tool)"}
    node_write["Tool Gateway: <Write Action>"]
    node_validate["Node: <Evidence & Schema Validator>"]
    node_out(["Verified Output (With Citations & Uncertainty Tags)"])
    node_fallback(["Fallback / Safe Refusal"])

    node_start -->|"Structured Request"| node_plan
    node_plan -->|"Select Action"| gw_tool
    gw_tool -->|"Read-Only Permitted"| node_read
    gw_tool -->|"Write Action Requested"| gw_approval
    gw_tool -.->|"Max Steps / Timeout Exceeded"| node_fallback
    node_read -->|"Tool Evidence"| node_validate
    gw_approval -->|"Approved by Human"| node_write
    gw_approval -.->|"Denied / Timeout"| node_fallback
    node_write -->|"Audit Record + Result"| node_validate
    node_validate -->|"Pass Grounding Check"| node_out
    node_validate -.->|"Hallucination / Invalid Citation"| node_fallback
```

## 3. Legend `[REQUIRED]`

- **Rounded Pill (`([...])`)**: Agent workflow entry, verified output, or safe-refusal terminal node.
- **Diamond (`{...}`)**: Deterministic policy guard, budget/iteration limit, or human-in-the-loop approval gate.
- **Solid vs. Dashed Arrows**: Nominal execution (`-->`) vs. budget exceeded, denial, or validation failure fallback (`-.->`).
