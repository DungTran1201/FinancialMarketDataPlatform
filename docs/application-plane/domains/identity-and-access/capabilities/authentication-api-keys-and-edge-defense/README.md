---
doc_id: CAP-APP-IAM-DOC-001
title: "Capability: Authentication, API Keys & Edge Defense (CAP-APP-IAM-001)"
doc_type: index
plane: application-plane
scope_level: capability
domain: identity-and-access
capability_id: CAP-APP-IAM-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/modules/iam/presentation/router.py"
    - "src/serving/api/modules/iam/domain/ports.py"
    - "src/serving/api/modules/iam/domain/security.py"
related_docs:
  - APP-DOM-IAM-001
  - CAP-APP-IAM-REQ-001
  - CAP-APP-IAM-COMP-001
  - CAP-APP-IAM-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Indexed all Governance V2 artifacts for CAP-APP-IAM-001."
---

# Capability: Authentication, API Keys & Edge Defense (`CAP-APP-IAM-001`)

> [!CAUTION]
> **Document Status `DRAFT` (Security Remediation Open)**: Critical RBAC enforcement, Postgres credential lookup, API key persistence, and default JWT secret hardening remain `NOT_IMPLEMENTED`.

## 1. Requirements, Use Cases & Workflows

- [capability.yaml](capability.yaml) — Capability manifest (`HIGH_CRITICAL`)
- [requirements/capability-specification.md](requirements/capability-specification.md) (`CAP-APP-IAM-REQ-001`)
- [requirements/business-rules.md](requirements/business-rules.md) (`CAP-APP-IAM-RULE-001`)
- [requirements/nfr.md](requirements/nfr.md) (`CAP-APP-IAM-NFR-001`)
- [use-cases/uc-iam-001-issue-and-verify-jwt.md](use-cases/uc-iam-001-issue-and-verify-jwt.md) (`UC-IAM-001`)
- [use-cases/uc-iam-002-revoke-jwt-and-mint-api-key.md](use-cases/uc-iam-002-revoke-jwt-and-mint-api-key.md) (`UC-IAM-002`)
- [use-cases/uc-iam-003-administer-domains-and-middleware.md](use-cases/uc-iam-003-administer-domains-and-middleware.md) (`UC-IAM-003`)
- [workflows/auth-token-and-middleware-sequence.md](workflows/auth-token-and-middleware-sequence.md) (`DIAG-APP-IAM-SEQ-001`)
- [workflows/auth-token-lifecycle-state.md](workflows/auth-token-lifecycle-state.md) (`DIAG-APP-IAM-STATE-001`)
- [workflows/auth-flow-swimlane.md](workflows/auth-flow-swimlane.md) (`DIAG-APP-IAM-FLOW-001`)

## 2. Design, Contracts, Data, Security & Quality

- [design/component-design.md](design/component-design.md) (`CAP-APP-IAM-COMP-001`)
- [contracts/openapi.yaml](contracts/openapi.yaml), [contracts/error-catalog.md](contracts/error-catalog.md), [contracts/data-contract.yaml](contracts/data-contract.yaml)
- [data/data-model.md](data/data-model.md), [data/database-design.md](data/database-design.md), [data/iam-erd.md](data/iam-erd.md)
- [security/threat-model.md](security/threat-model.md), [security/security-requirements.md](security/security-requirements.md), [security/authorization-matrix.yaml](security/authorization-matrix.yaml), [security/threat-model-diagram.md](security/threat-model-diagram.md)
- [quality/test-scenarios.md](quality/test-scenarios.md), [quality/test-cases.yaml](quality/test-cases.yaml), [quality/traceability.yaml](quality/traceability.yaml)
- Plane Shared Ops & Test Plan: [runbook.md](../../../../operations/runbook.md), [incident-and-recovery.md](../../../../operations/incident-and-recovery.md), [observability-and-slo.md](../../../../operations/observability-and-slo.md), [test-plan.md](../../../../operations/test-plan.md)
