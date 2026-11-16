---
doc_id: TPL-REQ-CAP-001
title: "Template: Capability Specification"
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
    - "docs/governance/templates/product-and-requirements/capability-specification.template.md"
related_docs:
  - GOV-ARCH-001
  - GOV-STD-AGENT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Capability Specification template linking capability.yaml manifest, scope, dependencies, and AS-IS vs TARGET summary."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Initial V2 capability specification template."
---

# Template: Capability Specification

Instantiated inside `docs/<plane>/domains/<domain>/capabilities/<capability>/` alongside `capability.yaml`.

---

# Capability Specification: `<Capability Name>` (`<CAP-DOM-NNN>`)

## 1. Capability Summary & Scope `[REQUIRED]`

- **Manifest**: `[capability.yaml](capability.yaml)`
- **Plane / Domain**: `<plane>` / `<domain>`
- **Risk Tier**: `<LOW | MEDIUM | HIGH_CRITICAL>`
- **In Scope**: `<Explicit functional scope>`
- **Out of Scope**: `<Explicitly excluded behavior>`

## 2. Actors, Triggers & Dependencies `[REQUIRED]`

- **Actors**: `<Who or what triggers this capability>`
- **Upstream Dependencies**: `<Capabilities, external APIs, or shared contracts>`
- **Downstream Consumers**: `<Dependent capabilities or clients>`

## 3. Current Implementation (`AS-IS`) vs. Target State (`TARGET`) `[REQUIRED]`

| Aspect | AS-IS Implementation State | Target Behavior | Evidence / Gap |
|---|---|---|---|
| `<Subsystem / Endpoint / Store>` | `IMPLEMENTED | PARTIALLY_IMPLEMENTED | SIMULATED | NOT_IMPLEMENTED` | `<Target state>` | `<Exact code/test file paths or gap note>` |

## 4. Artifact & Verification Links `[REQUIRED]`

Reference only the applicable files under `requirements/`, `use-cases/`, `design/`, `contracts/`, `data/`, `security/`, `quality/`, `operations/`, and `decisions/` (do not duplicate their contents here).
