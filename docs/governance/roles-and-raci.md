---
doc_id: GOV-POL-RACI-001
title: "Documentation Roles & RACI Ownership Matrix"
doc_type: governance
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: documentation-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/roles-and-raci.md"
related_docs:
  - GOV-POL-REV-001
  - GOV-POL-SOT-001
  - GOV-CAT-ART-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Defined exact RACI assignments across all 11 engineering roles and escalation rules for cross-role conflicts."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Initial Documentation V2 roles and RACI ownership matrix."
---

# Documentation Roles & RACI Ownership Matrix

Ownership MUST be assigned explicitly per artifact type. Statements asserting that "everyone is responsible" are prohibited.

## 1. Canonical Role Identifiers

- `documentation-architect` — Documentation Architect / Engineering Lead
- `business-analyst` — Senior Business Analyst / Requirements Engineer
- `system-architect` — System Architect / Solution Architect
- `fullstack-engineer` — Senior Fullstack Engineer
- `data-architect` — Data Architect / Senior Data Engineer
- `database-architect` — Database Architect / Database Engineer
- `ai-engineer` — Senior AI Engineer / AI Architect
- `security-architect` — Security Architect / Application Security Engineer
- `qa-lead` — QA Lead / Test Architect
- `devops-sre` — DevOps / SRE Engineer
- `documentation-tooling-engineer` — Documentation Tooling Engineer / Technical Writer

*(Legend: **R** = Responsible [executes authoring/update], **A** = Accountable [single final approval authority], **C** = Consulted, **I** = Informed).*

## 2. RACI Matrix by Artifact Category

| Artifact Category | Doc Arch | BA / Req | Sys Arch | Fullstack | Data Arch | DB Arch | AI Eng | Sec Arch | QA Lead | SRE | Tooling |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Documentation Architecture, Standards & Lifecycle | **R / A** | C | C | C | C | C | C | C | C | C | R |
| Templates, Schemas, `validate_docs.py` & Doc CI | **A** | C | C | I | I | I | I | C | C | I | **R** |
| Product Brief, Requirements (BR/FR), Use Cases, Rules | I | **R / A** | C | C | C | C | C | C | C | I | I |
| NFRs & Quality Targets | I | R | **A** | C | C | C | C | C | C | R | I |
| System Overview, Plane Architecture & ADRs | I | C | **R / A** | C | C | C | C | C | I | C | I |
| Component Design & HTTP API (`openapi.yaml`, Errors) | I | C | **A** | **R** | C | C | C | C | C | I | I |
| Data Architecture, Event Contracts (`asyncapi.yaml`, `data-contract.yaml`) & Lineage | I | C | C | C | **R / A** | C | C | C | C | C | I |
| Logical Data Model & Physical DB Design / Migrations | I | C | C | C | C | **R / A** | I | C | C | C | I |
| Agent Runtime, Workflows, Tool Contracts & Evals | I | C | **A** | C | C | I | **R** | C | C | C | I |
| Threat Model, Security Reqs & Authorization Matrix | I | C | C | C | C | C | C | **R / A** | C | I | I |
| Test Plan, Scenarios, Test Cases & Traceability | I | C | I | C | C | C | C | C | **R / A** | C | I |
| Deployment, Observability/SLOs, Runbooks & Recovery | I | I | C | C | C | C | C | C | C | **R / A** | I |

## 3. Conflict Escalation Rules

1. **Single-Domain Disputes**: Resolved by the single **Accountable (`A`)** role shown in Section 2.
2. **Security vs. Delivery/Usability Disputes**: Security controls for `HIGH`/`CRITICAL` risks require explicit `security-architect` approval or formal risk acceptance by the human system owner; no other role MAY waive security findings silently.
3. **Cross-Plane / Cross-Owner Disputes**: Coordinated by `documentation-architect` and `system-architect`; unresolved technical disputes MUST be formalized as an ADR, and unresolved business scope disputes MUST be logged as `OPEN` for human product sign-off.
