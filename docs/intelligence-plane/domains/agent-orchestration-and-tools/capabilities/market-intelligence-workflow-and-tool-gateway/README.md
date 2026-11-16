---
doc_id: CAP-INT-ORC-DOC-001
title: "Capability: Market Intelligence Workflow & Tool Gateway"
doc_type: index
plane: intelligence-plane
scope_level: capability
domain: agent-orchestration-and-tools
capability_id: CAP-INT-ORC-001
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/intelligence/orchestrator/graph.py"
    - "src/intelligence/workflows/investigation.py"
    - "src/intelligence/tools/contracts.py"
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
    - "src/intelligence/main.py"
related_docs:
  - INT-DOM-ORC-001
  - CAP-INT-ORC-REQ-001
  - CAP-INT-ORC-RULE-001
  - CAP-INT-ORC-NFR-001
  - CAP-INT-ORC-WF-001
  - CAP-INT-ORC-COMP-001
  - CAP-INT-ORC-AGT-001
  - CAP-INT-ORC-TM-001
  - CAP-INT-ORC-SEC-001
  - CAP-INT-ORC-TS-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Initialized CAP-INT-ORC-001 capability index linking manifest, requirements, use cases, workflows, design, data, security, quality, and operations."
---

# Capability: Market Intelligence Workflow & Tool Gateway (`CAP-INT-ORC-001`)

- **Manifest**: [capability.yaml](capability.yaml) (`HIGH_CRITICAL`, `AS-IS`: `SIMULATED`)
- **Upstream Consumer**: Application Plane `CAP-APP-AGT-001` ([Agent Run & Report Portal](../../../../../application-plane/domains/agent-experience-and-reporting/capabilities/agent-run-and-report-portal/README.md))
- **Authoritative Tool & State Contracts**: [tool-contracts.yaml](../../../../shared-contracts/tool-contracts.yaml) & [data-contract.yaml](../../../../shared-contracts/data-contract.yaml)

## 1. Requirements, Use Cases & Workflows

- [requirements/capability-specification.md](requirements/capability-specification.md) (`CAP-INT-ORC-REQ-001`) — Functional requirements (`FR-INT-*`), `AS-IS` vs `TARGET`, open questions.
- [requirements/business-rules.md](requirements/business-rules.md) (`CAP-INT-ORC-RULE-001`) — Deterministic tool, budget, provenance, and side-effect business rules (`BR-INT-*`, `RULE-INT-*`).
- [requirements/nfr.md](requirements/nfr.md) (`CAP-INT-ORC-NFR-001`) — Quality requirements and unresolved SLO/latency targets (`NFR-INT-*`).
- **Use Cases**:
  - [UC-INT-001: Execute On-Demand Market Investigation](use-cases/uc-int-001-execute-on-demand-investigation.md)
  - [UC-INT-002: Execute an Approved Agent Tool](use-cases/uc-int-002-execute-approved-agent-tool.md)
  - [UC-INT-003: Verify Evidence Provenance](use-cases/uc-int-003-verify-evidence-provenance.md)
  - [UC-INT-004: Synthesize and Persist an Analysis Report](use-cases/uc-int-004-synthesize-and-persist-report.md)
  - [UC-INT-005: Handle Invalid Symbol or Tool Execution Failure](use-cases/uc-int-005-handle-invalid-symbol-or-tool-failure.md)
- **Workflows & Diagrams**:
  - [workflows/workflow-specification.md](workflows/workflow-specification.md) (`CAP-INT-ORC-WF-001`)
  - [workflows/agent-workflow-diagram.md](workflows/agent-workflow-diagram.md) (`DIAG-INT-ORC-AGT-001`)
  - [workflows/agent-run-sequence.md](workflows/agent-run-sequence.md) (`DIAG-INT-ORC-SEQ-001`)
  - [workflows/tool-invocation-sequence.md](workflows/tool-invocation-sequence.md) (`DIAG-INT-ORC-SEQ-002`)
  - [workflows/workflow-state-diagram.md](workflows/workflow-state-diagram.md) (`DIAG-INT-ORC-STATE-001`)
  - [workflows/evidence-provenance-flow.md](workflows/evidence-provenance-flow.md) (`DIAG-INT-ORC-DFD-001`)

## 2. Design, Contracts, Data, Security & Quality

- **Design & Error Catalog**: [design/component-design.md](design/component-design.md), [design/agent-specification.md](design/agent-specification.md), [contracts/error-catalog.md](contracts/error-catalog.md).
- **Data & Persistence**: [data/data-model.md](data/data-model.md), [data/database-design.md](data/database-design.md), [data/agent-state-erd.md](data/agent-state-erd.md).
- **Security**: [security/threat-model.md](security/threat-model.md), [security/security-requirements.md](security/security-requirements.md), [security/authorization-matrix.yaml](security/authorization-matrix.yaml), [security/side-effect-and-approval-policy.md](security/side-effect-and-approval-policy.md), [security/threat-model-diagram.md](security/threat-model-diagram.md), [security/agent-tool-authorization-flow.md](security/agent-tool-authorization-flow.md).
- **Quality & Operations**: [quality/test-scenarios.md](quality/test-scenarios.md), [quality/test-cases.yaml](quality/test-cases.yaml), [quality/traceability.yaml](quality/traceability.yaml), plus [Plane Operations](../../../../operations/runbook.md).
