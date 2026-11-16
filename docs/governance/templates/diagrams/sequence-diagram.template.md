---
doc_id: TPL-DIAG-SEQ-001
title: "Template: UML Sequence Diagram"
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
    - "docs/governance/templates/diagrams/sequence-diagram.template.md"
related_docs:
  - GOV-STD-DIAG-001
  - GOV-STD-API-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created UML 2.5.1 sequence diagram template with alt/opt fragments for error and retry paths."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Initial V2 UML sequence diagram template."
---

# Template: UML Sequence Diagram

Use for multi-step synchronous or asynchronous call flows showing participant order, protocol messages, timeouts, retries, auth checks, and failure branches. Derived from a Component Design, Use Case, or API Contract. When instantiated, set `doc_type: diagram` and `source_of_truth.is_authoritative: false`.

---

# Diagram: `<Scenario / Flow Name> (Sequence)`

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-<SCOPE>-NNN` |
| **Title & Purpose** | `<Title — One-sentence interaction purpose>` |
| **Owner Role & Scope** | `<owner-role> / <capability|use-case>` |
| **Authoritative Source** | `[<Source Spec / Contract>](<relative/path/to/source>)` (`<DOC-ID>`) |
| **Notation** | `Mermaid sequenceDiagram` (`UML 2.5.1`) |
| **Version & Status** | `<X.Y.Z> — <DRAFT|IN_REVIEW|APPROVED|DEPRECATED>` |

## 2. Diagram `[REQUIRED]`

```mermaid
sequenceDiagram
    autonumber
    actor Caller as "<Caller / Client>"
    participant Gateway as "<API / Service Entry>"
    participant Store as "<Repository / Broker>"

    Caller->>+Gateway: "<PROTOCOL> <Operation>(<Key Inputs>)"
    Gateway->>Gateway: "<Validate Auth & Input Schema>"
    alt "<Authorized & Valid>"
        Gateway->>+Store: "<Query / Publish>"
        Store-->>-Gateway: "<Result / Ack>"
        Gateway-->>Caller: "<Success Response (200/202)>"
    else "<Unauthorized or Invalid>"
        Gateway-->>-Caller: "<Error Envelope (4xx)>"
    end
```

## 3. Legend `[REQUIRED]`

- **Solid Arrow (`->>`)**: Synchronous request/command.
- **Dashed Arrow (`-->>`)**: Return response or asynchronous acknowledgement.
- **`alt` / `else` Block**: Mutually exclusive execution paths governed by explicit precondition/error rules.
- **Lifeline Activation (`+` / `-`)**: Active processing window per participant.
