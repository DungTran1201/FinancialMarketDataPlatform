---
doc_id: CAP-DP-STR-002-ROOT
title: "Capability: Realtime Hot State, OLAP Projection & Anomaly Detection (CAP-DP-STR-002)"
doc_type: index
plane: data-plane
scope_level: capability
domain: event-streaming
capability_id: CAP-DP-STR-002
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
    - "src/streaming/consumers/hot_redis.py"
    - "src/streaming/consumers/analytics_ch.py"
    - "src/streaming/consumers/anomaly_detector.py"
related_docs:
  - DP-DOM-STR-001
  - CAP-DP-STR2-SPEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Indexed CAP-DP-STR-002 Hot Cache, ClickHouse sink, and statistical anomaly detection docs."
---

# Capability: Realtime Hot State, OLAP Projection & Anomaly Detection (`CAP-DP-STR-002`)

- **Manifest**: [capability.yaml](capability.yaml) (`HIGH_CRITICAL` — `SIMULATED` Python dicts)
- **Requirements & UC**: [capability-specification.md](requirements/capability-specification.md), [business-rules.md](requirements/business-rules.md), [nfr.md](requirements/nfr.md), [use-case-hot-olap-anomaly.md](use-cases/use-case-hot-olap-anomaly.md)
- **Design, Data & Contracts**: [component-design.md](design/component-design.md), [projection-dfd.md](design/projection-dfd.md), [data-model.md](data/data-model.md), [database-design.md](data/database-design.md), [olap-erd.md](data/olap-erd.md), [error-catalog.md](contracts/error-catalog.md), Plane [asyncapi.yaml](../../../../shared-contracts/asyncapi.yaml) & [data-contract.yaml](../../../../shared-contracts/data-contract.yaml)
- **Security & Quality**: [threat-model.md](security/threat-model.md), [security-requirements.md](security/security-requirements.md), [threat-model-diagram.md](security/threat-model-diagram.md), [test-scenarios.md](quality/test-scenarios.md), [test-cases.yaml](quality/test-cases.yaml), [traceability.yaml](quality/traceability.yaml)
