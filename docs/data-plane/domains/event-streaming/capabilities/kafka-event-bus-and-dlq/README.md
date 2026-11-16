---
doc_id: CAP-DP-STR-001-ROOT
title: "Capability: Kafka Event Bus & DLQ (CAP-DP-STR-001)"
doc_type: index
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-001
status: IN_REVIEW
implementation_status: SIMULATED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/streaming/infrastructure/kafka_broker.py"
    - "src/streaming/contracts/topics.py"
related_docs:
  - DP-DOM-STR-001
  - CAP-DP-STR1-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Indexed CAP-DP-STR-001 Kafka bus and DLQ documentation."
---

# Capability: Kafka Event Bus & DLQ (`CAP-DP-STR-001`)

- **Manifest**: [capability.yaml](capability.yaml) (`HIGH_CRITICAL` — `SIMULATED` in-process broker)
- **Specs**: [capability-specification.md](requirements/capability-specification.md), [business-rules.md](requirements/business-rules.md), [nfr.md](requirements/nfr.md), [use-case-streaming-bus.md](use-cases/use-case-streaming-bus.md)
- **Design & Security**: [component-design.md](design/component-design.md), [streaming-dfd.md](design/streaming-dfd.md), [error-catalog.md](contracts/error-catalog.md), [threat-model.md](security/threat-model.md), [security-requirements.md](security/security-requirements.md), [threat-model-diagram.md](security/threat-model-diagram.md)
- **Contracts, Quality & Ops**: [asyncapi.yaml](../../../../shared-contracts/asyncapi.yaml), [data-contract.yaml](../../../../shared-contracts/data-contract.yaml), [test-scenarios.md](quality/test-scenarios.md), [test-cases.yaml](quality/test-cases.yaml), [traceability.yaml](quality/traceability.yaml)
