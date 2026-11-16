---
doc_id: CAP-INT-ORC-DOC-001
title: "Capability: Market Intelligence Workflow & Tool Gateway (CAP-INT-ORC-001)"
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
    - "src/intelligence/tools/gateway.py"
    - "src/intelligence/reporting/validator.py"
related_docs:
  - INT-DOM-ORC-001
  - CAP-INT-ORC-REQ-001
  - CAP-INT-ORC-COMP-001
  - CAP-INT-ORC-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created CAP-INT-ORC-001 capability index linking manifest, requirements, use cases, workflows, design, data, security, and quality artifacts."
---

# Capability: Market Intelligence Workflow & Tool Gateway (`CAP-INT-ORC-001`)

- **Manifest**: [capability.yaml](capability.yaml) (`HIGH_CRITICAL` risk tier, `SIMULATED` `AS-IS`).
- **Requirements**: [requirements/capability-specification.md](requirements/capability-specification.md) (`CAP-INT-ORC-REQ-001`), [requirements/nfr.md](requirements/nfr.md) (`CAP-INT-ORC-NFR-001`).
- **Use Cases**:
  - [UC-INT-001: Execute On-Demand Market Investigation](use-cases/uc-int-001-execute-on-demand-investigation.md)
  - [UC-INT-002: Execute an Approved Agent Tool](use-cases/uc-int-002-execute-approved-agent-tool.md)
  - [UC-INT-003: Verify Evidence Provenance](use-cases/uc-int-003-verify-evidence-provenance.md)
  - [UC-INT-004: Synthesize and Persist an Analysis Report](use-cases/uc-int-004-synthesize-and-persist-report.md)
  - [UC-INT-005: Handle Invalid Symbol or Tool Execution Failure](use-cases/uc-int-005-handle-invalid-symbol-or-tool-failure.md)
- **Workflows & Diagrams**:
  - [workflows/agent-workflow-diagram.md](workflows/agent-workflow-diagram.md) (`DIAG-INT-ORC-FLOW-001`)
  - [workflows/agent-run-sequence.md](workflows/agent-run-sequence.md) (`DIAG-INT-ORC-SEQ-001`)
  - [workflows/tool-invocation-sequence.md](workflows/tool-invocation-sequence.md) (`DIAG-INT-ORC-TOOL-SEQ-001`)
  - [workflows/workflow-state-diagram.md](workflows/workflow-state-diagram.md) (`DIAG-INT-ORC-STATE-001`)
  - [workflows/evidence-provenance-flow.md](workflows/evidence-provenance-flow.md) (`DIAG-INT-ORC-PROV-001`)
- **Design & Contracts**:
  - [design/component-design.md](design/component-design.md) (`CAP-INT-ORC-COMP-001`)
  - [design/agent-specification.md](design/agent-specification.md) (`CAP-INT-ORC-AGENT-001`)
  - [contracts/error-catalog.md](contracts/error-catalog.md) (`CAP-INT-ORC-ERR-001`)
  - [../../../../shared-contracts/tool-contracts.yaml](../../../../shared-contracts/tool-contracts.yaml)
- **Data**: [data/data-model.md](data/data-model.md) (`CAP-INT-ORC-DM-001`), [data/agent-state-erd.md](data/agent-state-erd.md) (`DIAG-INT-ORC-ERD-001`).
- **Security**: [security/threat-model.md](security/threat-model.md), [security/security-requirements.md](security/security-requirements.md), [security/authorization-matrix.yaml](security/authorization-matrix.yaml), [security/threat-model-diagram.md](security/threat-model-diagram.md), [security/agent-tool-authorization-flow.md](security/agent-tool-authorization-flow.md).
- **Quality**: [quality/test-scenarios.md](quality/test-scenarios.md), [quality/test-cases.yaml](quality/test-cases.yaml), [quality/traceability.yaml](quality/traceability.yaml).

