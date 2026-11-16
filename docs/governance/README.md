---
doc_id: GOV-ROOT-001
title: "Documentation V2 Governance Subsystem"
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
    - "docs/governance/README.md"
related_docs:
  - DOC-ROOT-001
  - GOV-ARCH-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established Documentation V2 governance entrypoint indexing architecture, standards, catalog, templates, schemas, and lifecycle policies."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Created Phase 1 governance index."
---

# Documentation V2 Governance Subsystem

This directory is the single authoritative home for **Documentation V2 — Phase 1: Documentation Foundation**. It defines how documentation is structured, authored, reviewed, traced, validated, and evolved across `FinancialMarketDataPlatform`.

## 1. Governance Architecture & Policies

| Artifact | Purpose | Owner Role |
|---|---|---|
| [documentation-architecture.md](documentation-architecture.md) | Platform -> Plane -> Domain -> Capability hierarchy & Phase 2 target tree | `documentation-architect` |
| [documentation-lifecycle.md](documentation-lifecycle.md) | 9-stage documentation lifecycle & Document vs. Implementation status separation | `documentation-architect` |
| [change-management.md](change-management.md) | Documentation change intake, updates, deprecation & retirement workflow | `documentation-architect` |
| [versioning-and-status.md](versioning-and-status.md) | SemVer rules, `DRAFT..DEPRECATED` doc states & `PLANNED..VERIFIED` implementation states | `documentation-architect` |
| [source-of-truth-policy.md](source-of-truth-policy.md) | Authority precedence and conflict resolution across code, contracts, and docs | `documentation-architect` |
| [roles-and-raci.md](roles-and-raci.md) | 11-role RACI matrix and conflict-escalation ownership | `documentation-architect` |
| [review-and-approval.md](review-and-approval.md) | Risk-tiered peer/architect/security review and explicit human sign-off rules | `documentation-architect` |
| [definition-of-ready.md](definition-of-ready.md) | Entry criteria before starting Phase 2 capability authoring or code changes | `business-analyst` |
| [definition-of-done.md](definition-of-done.md) | Exit criteria for closing documentation and verification work | `qa-lead` |
| [quality-gates.md](quality-gates.md) | Mandatory automated and manual gates across lifecycle transitions | `documentation-tooling-engineer` |
| [traceability-and-impact-analysis.md](traceability-and-impact-analysis.md) | End-to-end bidirectional traceability and change impact analysis procedure | `business-analyst` |

## 2. Engineering Standards, Catalog, Schemas & Templates

- **Engineering Standards**: [standards/README.md](standards/README.md) (Normative register plus writing, requirements, architecture, diagrams, contracts, data/DB, security, QA, NFR/ops, and AI/agent discovery standards).
- **Artifact Catalog & Applicability**: [catalog/artifact-catalog.yaml](catalog/artifact-catalog.yaml) and [catalog/artifact-applicability-matrix.yaml](catalog/artifact-applicability-matrix.yaml).
- **Machine-Readable Schemas**: `docs/governance/schemas/` (`document-frontmatter`, `capability-manifest`, `artifact-catalog`, `artifact-applicability-matrix`, `docs-index`, `traceability`).
- **Reusable Templates**: [templates/README.md](templates/README.md) across `common/`, `product-and-requirements/`, `architecture/`, `interfaces-and-data/`, `security/`, `quality/`, `operations/`, and `diagrams/`.
- **Legacy Migration Records**: [migration/legacy-inventory.md](migration/legacy-inventory.md) and [migration/legacy-disposition.md](migration/legacy-disposition.md).

## 3. Validation Command

```powershell
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py
```
