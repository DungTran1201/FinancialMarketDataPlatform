---
doc_id: TPL-REQ-DOM-001
title: "Template: Domain Specification"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: business-analyst
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/product-and-requirements/domain-specification.template.md"
related_docs:
  - GOV-ARCH-001
  - GOV-STD-REQ-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Domain Specification template defining bounded context, domain entities, invariants, and capabilities."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial V2 domain specification template."
---

# Template: Domain Specification

Instantiated at `docs/<plane>/domains/<domain>/domain-specification.md`.

---

# Domain Specification: `<Domain Name>`

## 1. Domain Purpose & Bounded Context `[REQUIRED]`

- **Owning Plane**: `<data-plane | application-plane | intelligence-plane>`
- **Domain Owner Role**: `<role>`
- **Responsibility Boundary**: `<What this domain owns and explicitly does NOT own>`

## 2. Ubiquitous Vocabulary & Core Domain Entities `[REQUIRED]`

| Entity / Concept | Natural Key | Domain Invariants | Owning Capability |
|---|---|---|---|
| `<EntityName>` | `<natural_key_fields>` | `<Core invariant>` | `<CAP-...>` |

## 3. Domain-Wide Business Rules `[CONDITIONAL: Required if rules span multiple capabilities]`

| Rule ID | Rule Statement | Enforcement Point |
|---|---|---|
| `RULE-<DOM>-001` | `<Domain invariant>` | `<Boundary / validation layer>` |

## 4. Capabilities Owned by This Domain `[REQUIRED]`

| Capability ID | Capability Name | Risk Tier | Status | Manifest Link |
|---|---|---|---|---|
| `CAP-<DOM>-001` | `<Name>` | `MEDIUM` | `DRAFT` | `[capability.yaml](capabilities/<cap>/capability.yaml)` |

## 5. Cross-Domain & Cross-Plane Dependencies `[CONDITIONAL: Required when dependencies exist]`

- `<Upstream/Downstream domain or shared contract>`
