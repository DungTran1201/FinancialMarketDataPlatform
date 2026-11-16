---
doc_id: DOC-ROOT-001
title: "FinancialMarketDataPlatform Documentation V2"
doc_type: index
plane: platform
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
    - "docs/README.md"
related_docs:
  - GOV-ROOT-001
  - GOV-ARCH-001
  - GOV-STD-AGENT-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Replaced Documentation V1 master index with Documentation V2 Phase 1 entrypoint and mandatory Agent reading order."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-architect
    summary: "Initialized Documentation V2 Phase 1 root entrypoint."
---

# FinancialMarketDataPlatform — Documentation V2

**Current Documentation Phase**: **Phase 1 — Documentation Foundation** (Complete & Validated).
**Phase 2 Status**: **Not Started** (`overview/`, `data-plane/`, `application-plane/`, and `intelligence-plane/` are reserved in [documentation-architecture.md](governance/documentation-architecture.md) and MUST NOT be populated until Phase 2 is explicitly authorized).

## 1. Entrypoints

| Resource | Purpose |
|---|---|
| [docs-index.yaml](docs-index.yaml) | Machine-readable root index for Agent discovery and validation |
| [governance/README.md](governance/README.md) | Governance policies, engineering standards, templates, catalog, schemas, and migration reports |
| [governance/documentation-architecture.md](governance/documentation-architecture.md) | Plane -> Domain -> Capability documentation topology and ownership model |
| [governance/standards/ai-agent-and-discovery-standards.md](governance/standards/ai-agent-and-discovery-standards.md) | Agent documentation rules and capability discovery workflow |
| [../scripts/docs/validate_docs.py](../scripts/docs/validate_docs.py) | Automated schema, metadata, link, and applicability validator |

## 2. Mandatory Agent Reading Order

Before modifying any capability or specification, an Agent MUST follow this exact sequence (see [ai-agent-and-discovery-standards.md](governance/standards/ai-agent-and-discovery-standards.md)):

1. Read root documentation instructions ([AGENTS.md](../AGENTS.md) and this [docs/README.md](README.md)) plus [docs-index.yaml](docs-index.yaml).
2. Resolve the task's **Plane** (`data-plane`, `application-plane`, `intelligence-plane`, or `governance`).
3. Resolve the target **Domain** and **Capability** (via the Plane and Domain `README.md` indexes).
4. Read the relevant **Capability Manifest** (`capability.yaml`) to determine scope, risk tier, required artifacts, and open blockers.
5. Read only the authoritative requirements and upstream dependencies listed in `capability.yaml`.
6. Read only related diagrams, contracts (`openapi.yaml` / `asyncapi.yaml` / `data-contract.yaml`), and design artifacts.
7. Inspect relevant source code (`src/`, `frontend/`), infrastructure configs (`deploy/`), and tests (`tests/`) to verify `AS-IS` reality.
8. Perform impact analysis ([traceability-and-impact-analysis.md](governance/traceability-and-impact-analysis.md)) before modifying any file.
9. Update only the affected artifacts; never fabricate decisions, requirements, or verification evidence.
10. Run `python scripts/docs/validate_docs.py` and relevant code/doc tests before reporting completion.

## 3. Non-Negotiable Ground Rules

- **Missing or Contradictory Specs**: If an authoritative document is missing, contradictory, or unapproved, the Agent MUST record an explicit blocker / open question and MUST NOT invent business or architectural decisions.
- **Document vs. Implementation Status**: `status: APPROVED` reflects document sign-off only; runtime state MUST be tracked separately in `implementation_status` (`PLANNED | NOT_IMPLEMENTED | SIMULATED | PARTIALLY_IMPLEMENTED | IMPLEMENTED | VERIFIED`).
- **Legacy Reference Recovery**: Legacy V1 documentation (`docs-v1-legacy-2026-11-16`) was retired per [legacy-disposition.md](governance/migration/legacy-disposition.md) and remains auditable via Git tag history.
