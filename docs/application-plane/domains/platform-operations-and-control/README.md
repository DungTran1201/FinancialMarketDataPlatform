---
doc_id: APP-DOM-OPS-001
title: "Domain: Platform Operations, Observability & Gateway Control"
doc_type: index
plane: application-plane
scope_level: domain
domain: platform-operations-and-control
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/gateway/observability.py"
    - "src/serving/api/gateway/service.py"
    - "src/serving/api/services/data_plane.py"
    - "src/serving/api/modules/platform_config/presentation/router.py"
related_docs:
  - APP-ROOT-001
  - APP-DOM-OPS-SPEC-001
  - APP-DOM-OPS-GLOSS-001
  - CAP-APP-OPS-DOC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Created Platform Operations & Control domain covering Observatory REST/SSE/WS, DataPlatformV01 triggers, and Microservices dispatcher."
---

# Domain: Platform Operations, Observability & Gateway Control

## 1. Domain Documentation

- [domain-specification.md](domain-specification.md) (`APP-DOM-OPS-SPEC-001`)
- [glossary.md](glossary.md) (`APP-DOM-OPS-GLOSS-001`)

## 2. Capabilities

- [CAP-APP-OPS-001 — Observability, Control & Gateway](capabilities/observability-control-and-gateway/README.md) (`DRAFT` / `HIGH_CRITICAL`)
