---
doc_id: TPL-DIAG-DEP-001
title: "Template: Deployment & Runtime Topology Diagram"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: devops-sre
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/diagrams/deployment-diagram.template.md"
related_docs:
  - GOV-STD-DIAG-001
  - GOV-STD-NFR-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created deployment and network topology diagram template aligned with Compose/runtime infrastructure."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Initial V2 deployment topology diagram template."
---

# Template: Deployment & Runtime Topology Diagram

Use when documenting runtime containers, host ports, network segments, volumes, or deployment environments derived from a Deployment Description and verified against actual Compose/IaC definitions. When instantiated, set `doc_type: diagram` and `source_of_truth.is_authoritative: false`.

---

# Diagram: `<Environment / Plane> Deployment Topology`

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-<SCOPE>-NNN` |
| **Title & Purpose** | `<Title — One-sentence topology scope>` |
| **Owner Role & Scope** | `devops-sre / <platform|plane|capability>` |
| **Authoritative Source** | `[<Deployment Description>](<relative/path/to/deployment.md>)` (`<DOC-ID>`) |
| **Notation** | `Mermaid flowchart TB` (`Deployment Topology`) |
| **Version & Status** | `<X.Y.Z> — <DRAFT|IN_REVIEW|APPROVED|DEPRECATED>` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    ext_client["<Client / Browser / Operator>"]

    subgraph net_edge["Network Zone: <Ingress / Public Edge>"]
        svc_ui["<Frontend / Reverse Proxy> (Port XXXX)"]
        svc_api["<Application API Runtime> (Port YYYY)"]
    end

    subgraph net_internal["Network Zone: <Internal Data / Storage Tier>"]
        svc_broker["<Message Broker> (Port ZZZZ)"]
        svc_db[("<Stateful Store> (Volume: /data)")]
    end

    ext_client -->|"HTTP/WS :XXXX"| svc_ui
    svc_ui -->|"API Proxy /REST :YYYY"| svc_api
    svc_api -->|"Produce / Consume :ZZZZ"| svc_broker
    svc_api -->|"SQL / Cache Read-Write"| svc_db
```

## 3. Legend `[REQUIRED]`

- **Subgraph**: Docker network, security zone, or host boundary.
- **Port Label**: Verified container/host port from deployment configuration.
- **Explicit Implementation Tag**: Label unimplemented `TARGET` infrastructure separately if the diagram shows planned vs. active services.
