---
doc_id: TPL-DIAG-STATE-001
title: "Template: UML State Machine Diagram"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/diagrams/state-machine-diagram.template.md"
related_docs:
  - GOV-STD-DIAG-001
  - GOV-STD-REQ-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created UML 2.5.1 state machine diagram template for stateful entities, jobs, and lifecycle entities."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Initial V2 state machine diagram template."
---

# Template: UML State Machine Diagram

Use when an entity, job, session, run, or document possesses >=3 distinct lifecycle states with guarded transitions or failure/terminal states. When instantiated, set `doc_type: diagram` and `source_of_truth.is_authoritative: false`.

---

# Diagram: `<Entity / Job Name> State Machine`

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-<SCOPE>-NNN` |
| **Title & Purpose** | `<Title — One-sentence lifecycle scope>` |
| **Owner Role & Scope** | `<owner-role> / <capability>` |
| **Authoritative Source** | `[<Domain / Component Spec>](<relative/path/to/source.md>)` (`<DOC-ID>`) |
| **Notation** | `Mermaid stateDiagram-v2` (`UML 2.5.1`) |
| **Version & Status** | `<X.Y.Z> — <DRAFT|IN_REVIEW|APPROVED|DEPRECATED>` |

## 2. Diagram `[REQUIRED]`

```mermaid
stateDiagram-v2
    [*] --> InitialState : "Create / Initialize"
    InitialState --> ActiveState : "Validate & Start [Guard Condition]"
    ActiveState --> CompletedState : "Finish Successfully"
    ActiveState --> FailedState : "Exhaust Retries / Fatal Error"
    FailedState --> InitialState : "Manual Retry / Requeue"
    CompletedState --> [*]
    FailedState --> [*] : "Terminal Dead-Letter"
```

## 3. Legend `[REQUIRED]`

- **`[*]`**: Initial pseudostate (entry) or final terminal state (exit).
- **State Box**: Persisted lifecycle state matching the authoritative enum/code constants.
- **Transition Label (`Event [Guard]`)**: Trigger event plus optional guard rule (`RULE-...`).
