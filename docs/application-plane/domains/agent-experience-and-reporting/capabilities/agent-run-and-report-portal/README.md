---
doc_id: CAP-APP-AGT-DOC-001
title: "Capability: Agent Run & Report Portal (CAP-APP-AGT-001)"
doc_type: index
plane: application-plane
scope_level: capability
domain: agent-experience-and-reporting
capability_id: CAP-APP-AGT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: ai-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/agent_api/presentation/router.py"
    - "src/serving/api/modules/reporting/presentation/router.py"
    - "frontend/src/modules/ai-workspace/AiWorkspaceModule.ts"
related_docs:
  - APP-DOM-AGT-001
  - CAP-APP-AGT-REQ-001
  - CAP-APP-AGT-COMP-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Indexed all artifacts for CAP-APP-AGT-001."
---

# Capability: Agent Run & Report Portal (`CAP-APP-AGT-001`)

## 1. Requirements, Use Cases & Workflows

- [capability.yaml](capability.yaml) (`MEDIUM` with `cross_plane_dependencies: true`)
- [requirements/capability-specification.md](requirements/capability-specification.md) (`CAP-APP-AGT-REQ-001`)
- [requirements/nfr.md](requirements/nfr.md) (`CAP-APP-AGT-NFR-001`)
- [use-cases/uc-agt-001-trigger-and-stream-agent-run.md](use-cases/uc-agt-001-trigger-and-stream-agent-run.md) (`UC-AGT-001`)
- [use-cases/uc-agt-002-view-and-verify-structured-reports.md](use-cases/uc-agt-002-view-and-verify-structured-reports.md) (`UC-AGT-002`)
- [workflows/agent-run-portal-sequence.md](workflows/agent-run-portal-sequence.md) (`DIAG-APP-AGT-SEQ-001`)
- [workflows/agent-run-status-state.md](workflows/agent-run-status-state.md) (`DIAG-APP-AGT-STATE-001`)

## 2. Design, Contracts, Quality & Plane References

- [design/component-design.md](design/component-design.md) (`CAP-APP-AGT-COMP-001`)
- [contracts/openapi.yaml](contracts/openapi.yaml), [contracts/error-catalog.md](contracts/error-catalog.md)
- [quality/test-scenarios.md](quality/test-scenarios.md), [quality/test-cases.yaml](quality/test-cases.yaml), [quality/traceability.yaml](quality/traceability.yaml)
- Plane C4 & Ops: [application-c4-container.md](../../../../architecture/diagrams/application-c4-container.md), [runbook.md](../../../../operations/runbook.md), [test-plan.md](../../../../operations/test-plan.md)
