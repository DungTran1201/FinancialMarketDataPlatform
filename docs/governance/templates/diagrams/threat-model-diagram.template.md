---
doc_id: TPL-DIAG-TM-001
title: "Template: Security Threat Model & Trust Boundary Diagram"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/diagrams/threat-model-diagram.template.md"
related_docs:
  - GOV-STD-DIAG-001
  - GOV-STD-SEC-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created security threat model diagram template highlighting trust boundaries, assets, entry points, and controls."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Initial V2 threat model diagram template."
---

# Template: Security Threat Model & Trust Boundary Diagram

Use for all `HIGH_CRITICAL` risk capabilities, authentication/authorization modules, externally exposed endpoints, and write-capable Agent tools. Derived from the authoritative Threat Model document (`TPL-SEC-TM-001`). When instantiated, set `doc_type: diagram` and `source_of_truth.is_authoritative: false`.

---

# Diagram: `<Scope Name> Threat Model`

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-<SCOPE>-NNN` |
| **Title & Purpose** | `<Title — Trust boundaries, entry points, and threat vectors>` |
| **Owner Role & Scope** | `security-architect / <platform|plane|capability>` |
| **Authoritative Source** | `[<Threat Model Document>](<relative/path/to/threat-model.md>)` (`<DOC-ID>`) |
| **Notation** | `Mermaid flowchart TB` (`Trust Boundary DFD`) |
| **Version & Status** | `<X.Y.Z> — <DRAFT|IN_REVIEW|APPROVED|DEPRECATED>` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    actor_untrusted["<External / Untrusted Caller>"]

    subgraph tb_dmz["Trust Boundary 1: <Edge / API Gateway>"]
        ep_auth["<Auth / Token Guard> [SEC-SCOPE-001]"]
    end

    subgraph tb_core["Trust Boundary 2: <Application / Tool Core>"]
        svc_domain["<Protected Service / Tool Gateway>"]
        asset_secret[("<Protected Asset: Credentials / Sensitive Data>")]
    end

    actor_untrusted -->|"THR-001: Credential / Injection Surface"| ep_auth
    ep_auth -->|"Validated Identity + Scope"| svc_domain
    svc_domain -->|"THR-002: Least-Privilege Access [SEC-SCOPE-002]"| asset_secret
```

## 3. Legend `[REQUIRED]`

- **Subgraph (`Trust Boundary`)**: Privilege, network, or process isolation boundary across which inputs MUST be authenticated and validated.
- **`THR-###`**: Threat ID cross-referenced to `threat-model.md`.
- **`SEC-###`**: Mitigating control ID (`AS-IS` gaps MUST be marked `[GAP]` rather than implied implemented).
