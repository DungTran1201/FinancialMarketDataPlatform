---
doc_id: DIAG-APP-IAM-FLOW-001
title: "Cross-Functional Swimlane Flow: HTTP Defense & IAM Control"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/identity-and-access/capabilities/authentication-api-keys-and-edge-defense/use-cases/uc-iam-003-administer-domains-and-middleware.md"
related_docs:
  - CAP-APP-IAM-UC-001
  - CAP-APP-IAM-UC-003
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Rendered Mermaid Swimlane-style Flowchart (explicitly non-BPMN 2.0.2 XML) across Browser, Edge Middleware, and IAM Service."
---

# Cross-Functional Swimlane Flow: HTTP Defense & IAM Control

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-IAM-FLOW-001` |
| **Title & Purpose** | Swimlane-Style Request Validation Across SPA, Edge Middleware & IAM Router |
| **Owner Role & Scope** | `business-analyst / CAP-APP-IAM-001` |
| **Authoritative Source** | [uc-iam-003-administer-domains-and-middleware.md](../use-cases/uc-iam-003-administer-domains-and-middleware.md) (`CAP-APP-IAM-UC-003`) |
| **Notation** | `Mermaid Swimlane-style Flowchart (NOT formal BPMN 2.0.2 XML)` |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
flowchart TD
    subgraph lane_ui["Lane 1: SPA Browser (auth.service.ts)"]
        ui_start(["Open #/administration"])
        ui_default["Auto-assign fallback quant_admin (AS-IS GAP)"]
        ui_key["Call POST /api/v1/auth/api-keys"]
    end

    subgraph lane_mw["Lane 2: Edge Middleware (:8000 / :8005)"]
        gw_host{"Host & WAF Path/Query OK?"}
        gw_rate{"SlidingWindow Limit OK?"}
        err_edge(["400 / 403 / 429 Error"])
    end

    subgraph lane_iam["Lane 3: IAM Router & Domain"]
        iam_check{"Target Route RBAC? (MISSING)"}
        iam_exec["Generate Token / Key + Mask Domains"]
        ui_done(["200 Response + Security Headers"])
    end

    ui_start --> ui_default --> ui_key --> gw_host
    gw_host -->|"Yes"| gw_rate
    gw_host -->|"No"| err_edge
    gw_rate -->|"Yes"| iam_check
    gw_rate -->|"Exceeded"| err_edge
    iam_check -.->|"AS-IS: Skipped unconditionally"| iam_exec
    iam_exec --> ui_done
```

## 3. Legend

- **Notation Disclosure**: Uses Mermaid `flowchart TD` with subgraph lanes (`Swimlane-style Flowchart`); not serialized as OMG BPMN 2.0.2 XML.
- **Dashed Transition (`-.->`)**: Documents unauthenticated pass-through into `iam_exec` because route-level RBAC `Depends` is `NOT_IMPLEMENTED`.
