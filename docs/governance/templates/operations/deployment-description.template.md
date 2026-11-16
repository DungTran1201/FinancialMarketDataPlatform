---
doc_id: TPL-OPS-DEP-001
title: "Template: Deployment Description"
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
    - "docs/governance/templates/operations/deployment-description.template.md"
related_docs:
  - GOV-STD-NFR-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Deployment Description template documenting runtime profiles, network zones, env vars, healthchecks, and rollback."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Initial V2 Deployment Description template."
---

# Template: Deployment Description

Describes runtime containers, Compose/Kubernetes profiles, network isolation, healthchecks, and deployment verification without repeating secret values.

---

# Deployment Description: `<Plane or Capability Name>`

## 1. Runtime Services & Profiles `[REQUIRED]`

| Service Name | Image / Dockerfile | Compose Profile | Network Zones | Ports (Internal / Host) | Healthcheck |
|---|---|---|---|---|---|
| `<service>` | `<Dockerfile>` | `<profile>` | `<network>` | `<port>` | `<probe endpoint/cmd>` |

## 2. Configuration & Secret Injection `[REQUIRED]`

- List required environment variables by name and purpose (refer to `.env.example` or secret store; NEVER commit secret values).

## 3. Deployment Diagram & Dependencies `[CONDITIONAL: Required when adding containers/networks]`

- `[<deployment-diagram.md>](<deployment-diagram.md>)`

## 4. Rollout & Rollback Procedure `[REQUIRED]`

- `<Exact deploy order, smoke checks, and deterministic rollback commands>`
