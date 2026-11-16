---
doc_id: GOV-STD-ROOT-001
title: "Engineering Documentation Standards Index"
doc_type: index
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: documentation-architect
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/standards/README.md"
related_docs:
  - GOV-ROOT-001
  - GOV-STD-REG-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created index for Documentation V2 Phase 1 engineering and documentation standards."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Initial standards index."
---

# Engineering Documentation Standards

All Phase 2 engineering specifications, contracts, models, diagrams, test suites, and runbooks MUST conform to the normative rules defined in this directory.

| Document | Standard Scope | Owner Role |
|---|---|---|
| [standards-register.md](standards-register.md) | External reference standards, versions, official URLs, revision status & governance scope | `documentation-architect` |
| [writing-standards.md](writing-standards.md) | Normative keywords, language, formatting, file naming, IDs, metadata, UTC dates, assumptions | `documentation-tooling-engineer` |
| [requirements-standards.md](requirements-standards.md) | BR, FR, NFR, Business Rules, Use Cases, AC, constraints, priorities & traceability rules | `business-analyst` |
| [architecture-standards.md](architecture-standards.md) | arc42 adaptation, viewpoints, ADRs, constraints, trade-offs, AS-IS vs. TARGET separation | `system-architect` |
| [diagram-standards.md](diagram-standards.md) | C4, BPMN, UML, ERD, DFD, Deployment, Threat Model & Agent Workflow rules + syntax | `system-architect` |
| [api-and-event-contract-standards.md](api-and-event-contract-standards.md) | OpenAPI 3.1.0, AsyncAPI 3.1.0, error models, auth, idempotency, versioning, evolution | `fullstack-engineer` |
| [data-and-database-standards.md](data-and-database-standards.md) | Conceptual/Logical/Physical models, App OLTP vs Data Plane storage, lineage & quality | `data-architect` |
| [security-standards.md](security-standards.md) | Threat modeling, trust boundaries, authorization matrix, secrets & PII prohibition | `security-architect` |
| [qa-and-testing-standards.md](qa-and-testing-standards.md) | Strategy, Plan, Scenario, Case, Data, Evidence separation, entry/exit criteria & DoD | `qa-lead` |
| [nfr-and-operations-standards.md](nfr-and-operations-standards.md) | 10 quality attributes, SLI/SLO rules (no invented targets), recovery & runbook rules | `devops-sre` |
| [ai-agent-and-discovery-standards.md](ai-agent-and-discovery-standards.md) | Agent runtime/tool/memory/eval documentation rules & 10-step Agent discovery workflow | `ai-engineer` |
