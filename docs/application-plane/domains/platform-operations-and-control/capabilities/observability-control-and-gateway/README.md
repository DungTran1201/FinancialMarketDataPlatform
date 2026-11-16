---
doc_id: CAP-APP-OPS-DOC-001
title: "Capability: Observability, Control & Gateway (CAP-APP-OPS-001)"
doc_type: index
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
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
related_docs:
  - APP-DOM-OPS-001
  - CAP-APP-OPS-REQ-001
  - CAP-APP-OPS-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Indexed all Governance V2 artifacts for CAP-APP-OPS-001."
---

# Capability: Observability, Control & Gateway (`CAP-APP-OPS-001`)

> [!WARNING]
> **Document Status `DRAFT` (Security Remediation Open)**: Unauthenticated access to `/observability/demo/emit`, `/live/probe`, `/data-platform/v01/run`, and `/microservices/dispatch/{service_id}` enables unauthorized compute/SSRF abuse.

## 1. Requirements, Use Cases & Workflows

- [capability.yaml](capability.yaml) (`HIGH_CRITICAL`)
- [requirements/capability-specification.md](requirements/capability-specification.md) (`CAP-APP-OPS-REQ-001`)
- [requirements/business-rules.md](requirements/business-rules.md) (`CAP-APP-OPS-RULE-001`)
- [requirements/nfr.md](requirements/nfr.md) (`CAP-APP-OPS-NFR-001`)
- [use-cases/uc-ops-001-dashboard-live-probe-and-streams.md](use-cases/uc-ops-001-dashboard-live-probe-and-streams.md) (`UC-OPS-001`)
- [use-cases/uc-ops-002-data-flow-dag-traces-and-simulation.md](use-cases/uc-ops-002-data-flow-dag-traces-and-simulation.md) (`UC-OPS-002`)
- [use-cases/uc-ops-003-gateway-dispatch-and-v01-pipeline.md](use-cases/uc-ops-003-gateway-dispatch-and-v01-pipeline.md) (`UC-OPS-003`)
- [workflows/observability-ws-sse-sequence.md](workflows/observability-ws-sse-sequence.md) (`DIAG-APP-OPS-SEQ-001`)
- [workflows/ops-control-swimlane.md](workflows/ops-control-swimlane.md) (`DIAG-APP-OPS-FLOW-001`)
- [workflows/pipeline-execution-state.md](workflows/pipeline-execution-state.md) (`DIAG-APP-OPS-STATE-001`)

## 2. Design, Contracts, Security & Quality

- [design/component-design.md](design/component-design.md) (`CAP-APP-OPS-COMP-001`), [design/observability-dfd.md](design/observability-dfd.md) (`DIAG-APP-OPS-DFD-001`)
- [contracts/openapi.yaml](contracts/openapi.yaml), [contracts/asyncapi.yaml](contracts/asyncapi.yaml), [contracts/data-contract.yaml](contracts/data-contract.yaml), [contracts/error-catalog.md](contracts/error-catalog.md)
- [security/threat-model.md](security/threat-model.md), [security/security-requirements.md](security/security-requirements.md), [security/threat-model-diagram.md](security/threat-model-diagram.md)
- [quality/test-scenarios.md](quality/test-scenarios.md), [quality/test-cases.yaml](quality/test-cases.yaml), [quality/traceability.yaml](quality/traceability.yaml)
- Plane C4 & Ops: [application-c4-container.md](../../../../architecture/diagrams/application-c4-container.md), [runbook.md](../../../../operations/runbook.md), [incident-and-recovery.md](../../../../operations/incident-and-recovery.md), [observability-and-slo.md](../../../../operations/observability-and-slo.md), [test-plan.md](../../../../operations/test-plan.md)
