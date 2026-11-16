---
doc_id: CAP-APP-OPS-SEC-001
title: "Security Requirements: Observability, Control & Gateway"
doc_type: specification
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/gateway/observability.py"
    - "src/serving/api/gateway/service.py"
related_docs:
  - CAP-APP-OPS-TM-001
  - APP-ARCH-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Defined mandatory RBAC, dispatch allowlist, and stream limit security requirements."
---

# Security Requirements: Observability, Control & Gateway

## 1. Mandatory Security Controls & Gap Status

| Sec Req ID | Control Statement | `AS-IS` Status |
|---|---|---|
| `SEC-OPS-001` | Mutating control triggers (`POST /demo/emit`, `/live/probe`, `/data-platform/v01/{run,compaction}`, `/microservices/dispatch/{id}`) MUST require verified `operator` or `admin` RBAC tokens. | `NOT_IMPLEMENTED` (`BLOCKED`) |
| `SEC-OPS-002` | `POST /microservices/dispatch/{service_id}` MUST restrict dispatch paths via allowlist and deny arbitrary admin/internal mutation forwarding (`THR-OPS-002`). | `NOT_IMPLEMENTED` |
| `SEC-OPS-003` | `WS /ws/v1/observability/stream` and SSE `/stream` SHOULD authenticate handshakes and cap concurrent subscribers per IP hash (`THR-OPS-004`). | `NOT_IMPLEMENTED` |
| `SEC-OPS-004` | `/api/v1/health/ready` masks Redis/ClickHouse/Postgres/Kafka credentials cleanly (`IPAndEndpointCipher`) but MUST execute non-mutating liveness checks rather than returning hardcoded `"ready"`. | `PARTIALLY_IMPLEMENTED` |

## 2. Threat Traceability & Gate Status

- Linked threat scenarios: `THR-OPS-001` through `THR-OPS-004` in [threat-model.md](threat-model.md). Status remains `DRAFT` (`BLOCKED`) pending RBAC dependency injection.
