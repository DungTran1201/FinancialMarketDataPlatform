---
doc_id: "DOC-API-ROOT"
title: "API & Integration Contracts Index"
version: "1.0.0"
status: "DRAFT"
implementation_status: "PLANNED"
owner: "API Architect"
purpose: "Phase 3+ specification domain for REST OpenAPI contracts, WebSocket/SSE stream schemas, NATS JetStream subjects, Auth/RBAC, and error formats."
scope: "External HTTP/WS APIs and internal persistent messaging interfaces."
dependencies:
  - "docs/product/srs.md"
  - "docs/architecture/README.md"
references:
  - "docs/data-engineering/README.md"
assumptions:
  - "Detailed OpenAPI/AsyncAPI contracts authored in Phase 3."
open_issues:
  - "JWT vs local API key rotation workflow details finalized in Phase 3."
review_criteria:
  - "100% protected endpoints require explicit RBAC claims and deterministic Decimal string serialization"
---

# API & Integration (`docs/api-and-integration/`)

Phase 3 home for formal boundary contracts:
- REST OpenAPI 3.1 specifications
- WebSocket / SSE real-time stream envelope & conflation policy
- NATS JetStream subjects, retention, and consumer group specifications
- Authentication, RBAC capabilities matrix & standard error contracts
