---
doc_id: OVR-ROOT-001
title: "Platform Overview — System Context, Architecture & Cross-Plane Documentation"
doc_type: index
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/overview/README.md"
related_docs:
  - DOC-ROOT-001
  - OVR-PROD-001
  - OVR-CTX-001
  - OVR-REQ-001
  - OVR-ARCH-3P-001
  - OVR-ARCH-XPL-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Initialized Phase 2 platform overview index linking product context, system context, 3-plane architecture, cross-plane interactions, ADRs, and diagrams."
---

# FinancialMarketDataPlatform — System Overview

This scope establishes the platform-wide context, boundaries, system requirements, three-plane ownership model, cross-plane interaction contracts, and architectural decisions for `FinancialMarketDataPlatform`.

## 1. Authoritative Overview Documents

| Document | Scope & Responsibility | Status | Implementation Status |
|---|---|---|---|
| [product-context.md](product-context.md) | Product purpose, users, platform scope, out-of-scope, known limitations | `IN_REVIEW` | `PARTIALLY_IMPLEMENTED` |
| [system-context.md](system-context.md) | External actors, Binance integration, infrastructure boundaries, trust boundaries | `IN_REVIEW` | `PARTIALLY_IMPLEMENTED` |
| [system-requirements.md](system-requirements.md) | Platform-level BR/FR/NFR/CON/SEC/OPS index (`SYS-*`) tracing down to Planes | `DRAFT` | `PARTIALLY_IMPLEMENTED` |
| [three-plane-architecture.md](three-plane-architecture.md) | Ownership, allowed/prohibited dependencies & failure isolation across Planes | `IN_REVIEW` | `PARTIALLY_IMPLEMENTED` |
| [cross-plane-interactions.md](cross-plane-interactions.md) | Cross-plane provider/consumer contract matrix & interaction semantics | `IN_REVIEW` | `PARTIALLY_IMPLEMENTED` |
| [platform-dependencies.md](platform-dependencies.md) | Python/Node dependencies, external infra runtime state & shared kernel coupling | `IN_REVIEW` | `PARTIALLY_IMPLEMENTED` |
| [glossary.md](glossary.md) | Platform ubiquitous terminology aligned with codebase symbols | `IN_REVIEW` | `NOT_APPLICABLE` |
| [architecture-overview.md](architecture/architecture-overview.md) | System-wide runtime container structure (`AS-IS` monolith vs compose topology) | `IN_REVIEW` | `PARTIALLY_IMPLEMENTED` |
| [architecture-quality-attributes.md](architecture/architecture-quality-attributes.md) | System reliability, availability, scalability, security & open quality targets | `DRAFT` | `PARTIALLY_IMPLEMENTED` |
| [decisions/README.md](architecture/decisions/README.md) | Cross-plane Architecture Decision Records (`ADR-OVR-001..003`) | `DRAFT` | `PARTIALLY_IMPLEMENTED` |

## 2. Overview Diagrams (`is_authoritative: false`)

- [system-context.md](diagrams/system-context.md) (`DIAG-OVR-CTX-001` — C4 Level 1 System Context)
- [c4-container.md](diagrams/c4-container.md) (`DIAG-OVR-CONT-001` — C4 Level 2 Container Topology)
- [three-plane-architecture.md](diagrams/three-plane-architecture.md) (`DIAG-OVR-3P-001` — Plane Ownership & Allowed Dependencies)
- [cross-plane-interaction.md](diagrams/cross-plane-interaction.md) (`DIAG-OVR-XPL-001` — Cross-Plane Request, Streaming & Agent Sequence)
- [deployment-context.md](diagrams/deployment-context.md) (`DIAG-OVR-DEP-001` — Compose Profiles, Ports & Network Zones)

## 3. Plane Entrypoints

- **Data Plane**: [../data-plane/README.md](../data-plane/README.md)
- **Application Plane**: [../application-plane/README.md](../application-plane/README.md)
- **Intelligence Plane**: [../intelligence-plane/README.md](../intelligence-plane/README.md)
