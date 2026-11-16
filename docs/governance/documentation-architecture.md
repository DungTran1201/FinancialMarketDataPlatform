---
doc_id: GOV-ARCH-001
title: "Documentation V2 Architecture & Phase 2 Target Hierarchy"
doc_type: architecture
plane: governance
scope_level: platform
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
    - "Documentation V2 Phase 1 Governance Architecture"
related_docs:
  - DOC-ROOT-001
  - GOV-ROOT-001
  - GOV-STD-WRIT-001
  - GOV-POL-SOT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Defined Documentation V2 Plane->Domain->Capability architecture, ownership boundaries, and Phase 2 target tree."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Initial Documentation V2 architecture replacing legacy monolithic docs/ and separate models/ directories."
---

# Documentation V2 Architecture & Phase 2 Target Hierarchy

## 1. Architectural Purpose

Documentation V2 organizes all engineering knowledge around **architectural ownership and independent capability delivery** rather than monolithic cross-system documents or duplicated phase folders. Every specification MUST live at the narrowest ownership boundary that fully owns its lifecycle:

`Platform -> Plane -> Domain -> Capability -> Use Case / Component -> Engineering Artifacts`

This architecture MUST prevent:

- Giant monolithic SRS, architecture, or API files covering the entire system.
- Competing documentation hierarchies (such as a separate `docs/archive/`, global `docs/diagrams/` detached from scope, or parallel `models/` and `docs/contracts/` duplicating specifications).
- Empty placeholder directories for hypothetical domains or capabilities.

---

## 2. Phase 1 Active Foundation vs. Phase 2 Target Structure

### 2.1 Phase 1 Active Tree (Implemented Now)

Only the Documentation Foundation exists during Phase 1:

- `docs/README.md` — Documentation V2 root entrypoint and Agent reading order.
- `docs/docs-index.yaml` — Machine-readable root index for automated discovery and validation.
- `docs/governance/` — Standards, templates, schemas, artifact catalog, applicability matrix, lifecycle policies, and legacy migration records.
- `scripts/docs/validate_docs.py` — Automated validator enforcing schemas, metadata, links, applicability, and scope boundaries.

### 2.2 Phase 2 Target Tree (Reserved — NOT Created in Phase 1)

Phase 2 MUST populate system, plane, domain, and capability documentation using the following uniform hierarchy across all three planes (`data-plane`, `application-plane`, `intelligence-plane`):

```text
docs/
├── README.md
├── docs-index.yaml
├── governance/
├── overview/                         # System-wide context, cross-plane boundaries, glossary, top-level ADRs
├── data-plane/
│   ├── README.md
│   ├── architecture/
│   ├── domains/
│   │   └── <domain>/
│   │       ├── README.md
│   │       ├── domain-specification.md
│   │       └── capabilities/
│   │           └── <capability>/
│   │               ├── README.md
│   │               ├── capability.yaml
│   │               ├── requirements/
│   │               ├── use-cases/
│   │               ├── workflows/
│   │               ├── design/
│   │               ├── contracts/
│   │               ├── data/
│   │               ├── security/
│   │               ├── quality/
│   │               ├── operations/
│   │               └── decisions/
│   ├── shared-contracts/
│   ├── operations/
│   └── decisions/
├── application-plane/
│   ├── README.md
│   ├── architecture/
│   ├── domains/
│   │   └── <domain>/
│   │       └── capabilities/
│   │           └── <capability>/
│   │               └── ...
│   ├── shared-contracts/
│   ├── operations/
│   └── decisions/
└── intelligence-plane/
    ├── README.md
    ├── architecture/
    ├── domains/
    │   └── <domain>/
    │       └── capabilities/
    │           └── <capability>/
    │               └── ...
    ├── shared-contracts/
    ├── operations/
    └── decisions/
```

**Phase 1 Rule**: Empty folders for `<domain>` or `<capability>` MUST NOT be created ahead of actual Phase 2 authoring. Within any future `<capability>/`, only folders required or applicable under [artifact-applicability-matrix.yaml](catalog/artifact-applicability-matrix.yaml) SHOULD be created.

---

## 3. Ownership & Boundary Rules by Scope Level

| Scope Level | Path Pattern (Phase 2) | Primary Owner | Explicit Scope & Anti-Duplication Rules |
|---|---|---|---|
| **Governance** | `docs/governance/` | Documentation Architect | MUST own standards, templates, catalog, schemas, lifecycle, and migration records only. MUST NOT contain Phase 2 product or plane designs. |
| **Platform Overview** | `docs/overview/` | System Architect | MUST own system-wide C4 Level 1 context, cross-plane dependency rules, platform glossary, and cross-plane ADRs. MUST NOT duplicate internal plane component details. |
| **Plane** | `docs/<plane>/` | Plane Architect (`data-architect`, `system-architect`, `ai-engineer`) | MUST own internal plane architecture (`architecture/`), contracts shared by multiple domains within that plane (`shared-contracts/`), plane-wide runbooks/SLOs (`operations/`), and plane ADRs (`decisions/`). |
| **Domain** | `docs/<plane>/domains/<domain>/` | Domain Owner | MUST own domain bounded context, ubiquitous language, domain-wide entities/business rules (`domain-specification.md`), and domain navigation (`README.md`). |
| **Capability** | `docs/<plane>/domains/<domain>/capabilities/<capability>/` | Capability Owner | MUST own `capability.yaml` plus risk-applicable artifacts (`requirements/`, `use-cases/`, `workflows/`, `design/`, `contracts/`, `data/`, `security/`, `quality/`, `operations/`, `decisions/`). |
| **Use Case / Component** | Inside `<capability>/use-cases/` or `design/` | Business Analyst / Fullstack Engineer | Each use case MUST own its discrete actor-goal interaction specification; each non-trivial component MUST own its internal design without duplicating capability requirements. |

---

## 4. Placement Rules for Contracts, Diagrams & Executable Assets

1. **Single Canonical Contract Owner**: Every HTTP API (`openapi.yaml`) and asynchronous event contract (`asyncapi.yaml`, `data-contract.yaml`) MUST have exactly one canonical owner (Capability `contracts/` if single-capability, or `<plane>/shared-contracts/` if shared across domains). Consumers MUST reference the canonical file rather than copying schemas into Markdown.
2. **Scoped Diagram Placement**: Diagrams MUST live adjacent to the scope they visualize (for example, `overview/diagrams/` for system context, `<plane>/architecture/diagrams/` for C4 containers, `<capability>/design/` or `workflows/` for sequences, state machines, ERDs, and BPMN flows). A detached repository-wide `docs/diagrams/` tree MUST NOT be recreated.
3. **Executable Schemas & Code Assets**: Runtime code (`src/`, `frontend/`), DDL (`deploy/postgres/`, `deploy/clickhouse/`), topic bootstrap scripts (`deploy/kafka/`), dbt models (`src/lakehouse/gold/dbt/`), and Iceberg configs (`deploy/iceberg/`) remain authoritative for `AS-IS` runtime behavior and stay alongside code/deployment assets. Documentation describes and links to them without claiming target designs are already implemented.
4. **History via Git**: Retired documentation MUST be tracked in Git history (`docs-v1-legacy-2026-11-16`) and migration records (`docs/governance/migration/`), NEVER in an active `docs/archive/` directory.
