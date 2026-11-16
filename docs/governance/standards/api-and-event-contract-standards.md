---
doc_id: GOV-STD-API-001
title: "API & Event Contract Documentation Standards"
doc_type: standard
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
    - "docs/governance/standards/api-and-event-contract-standards.md"
related_docs:
  - GOV-STD-REG-001
  - GOV-STD-DATA-001
  - GOV-STD-SEC-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established OpenAPI 3.1.0 and AsyncAPI 3.1.0 rules, single-source contract ownership, error catalogs, idempotency, and schema evolution policies."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Initial Documentation V2 API and event contract standard."
---

# API & Event Contract Documentation Standards

## 1. Machine-Readable Contract Primacy

1. **HTTP APIs** MUST be specified using **OpenAPI `3.1.0`** ([openapi.template.yaml](../templates/interfaces-and-data/openapi.template.yaml)).
2. **Asynchronous / Event-Driven Interfaces** (Kafka topics, WebSockets, SSE streams) MUST be specified using **AsyncAPI `3.1.0`** ([asyncapi.template.yaml](../templates/interfaces-and-data/asyncapi.template.yaml)) and/or a Data Contract ([data-contract.template.yaml](../templates/interfaces-and-data/data-contract.template.yaml)).
3. **No Prose Duplication**: Field-level JSON schemas, status codes, and payload examples MUST NOT be copied into Markdown tables when an authoritative OpenAPI or AsyncAPI file exists; Markdown capability/design documents MUST link directly to the canonical YAML file and summarize behavioral semantics only.

## 2. HTTP API Conventions (`OpenAPI 3.1.0`)

Every HTTP endpoint specification MUST define:

- **Naming & Paths**: Versioned prefix (`/api/v1/...`), lowercase `kebab-case` plural resource nouns, path parameters for entity lookup, and query parameters for filtering/pagination.
- **Operation IDs**: Unique `operationId` (`<domain>_<verb>_<resource>`) matching backend handler naming.
- **Request & Response Schemas**: JSON Schema Draft 2020-12 types; exact monetary/quantity values MUST be typed as decimal strings (`type: string`, `format: decimal`) rather than binary IEEE-754 floats; timestamps MUST specify ISO-8601 UTC (`format: date-time`).
- **Standardized Error Model**: All `4xx`/`5xx` error responses MUST conform to RFC 9457 / RFC 7807 problem/error envelope semantics and reference an entry in the capability or plane Error Catalog ([error-catalog.template.md](../templates/interfaces-and-data/error-catalog.template.md)).
- **Authentication & Authorization Declarations**: Every operation MUST explicitly declare `security` schemes (`bearerAuth` / `apiKeyAuth` or explicit `security: []` for intentionally public health probes) and map to a documented capability/RBAC rule in the authorization matrix.
- **Pagination & Bounded Queries**: Collection endpoints MUST declare bounded `limit` defaults/maximums, cursor or time-range boundaries, and `422` rejection behavior on unbounded scans.
- **Idempotency & Concurrency**: State-mutating `POST`/`PUT`/`PATCH` operations SHOULD specify `Idempotency-Key` header semantics, natural keys, or ETag/optimistic concurrency expectations; `202 Accepted` operations MUST document whether work executes truly asynchronously or synchronously.
- **Versioning & Backward Compatibility**: Breaking changes (removing required fields, narrowing types, changing endpoint URI semantics) MUST increment the major API version (`/api/v2/`) and record a deprecation window on `/api/v1/`.

## 3. Event-Driven Contract Conventions (`AsyncAPI 3.1.0`)

Every event-driven contract MUST define:

- **Channel & Operation Decoupling**: Use AsyncAPI `3.1.0` `channels` (transport address, partition strategy, retention) separate from `operations` (`action: send` vs `action: receive`).
- **Standard Envelope & Payload**: Explicitly declare `schema_version`, deterministic `event_id` derivation, `exchange_event_time` vs `ingested_at` UTC semantics, natural key, and partition key.
- **Producer & Consumer Ownership**: Every channel MUST identify one authoritative producer owner role and list known consumer groups with delivery semantics (`at-least-once` + idempotent sink key, manual commit boundaries, and DLQ routing).
- **Schema Evolution & Deprecation**: Additive optional fields MAY evolve under minor versions; breaking payload changes MUST introduce a new versioned channel/topic suffix (`.v2`), a dual-write or migration plan, and a deprecation sunset date.
