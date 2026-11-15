# Target Documentation Architecture & Reader Journey (`DOCS-002`)

| Metadata | Value |
|---|---|
| **Work Item** | `DOCS-002-documentation-architecture-reorganization` |
| **Architectural Model** | Domain & Reader-Journey Centric Documentation Framework |
| **Preservation Rule** | 100% Backward Compatible (Zero broken links, zero renumbered IDs) |
| **Updated Date** | 2026-11-15 |

---

## 1. Vision & Architectural Philosophy

The **FinancialMarketDataPlatform** documentation architecture is organized around **Engineering Domains and Reader Journeys**, eliminating cognitive overhead while preserving 100% of the project's technical specifications, canonical models, and historical decision records.

Instead of forcing developers to navigate through 15 abstract product lifecycle folders to find a technical contract or operational runbook, the documentation space is divided into 9 clear top-level domains:

```text
docs/
├── README.md                           # Master Documentation Portal & Journey Map
│
├── overview/                           # 1. ORIENTATION: System overview, tech stack, quick start
│   ├── README.md
│   ├── system-overview.md
│   ├── architecture-overview.md
│   └── technology-stack.md
│
├── architecture/                       # 2. ARCHITECTURE: Deep technical baselines, ADRs & domain deep-dives
│   ├── README.md
│   ├── 00-architecture-overview.md ... 14-data-platform-v01-and-microservices-architecture.md
│   └── adr/
│       ├── README.md
│       └── ADR-001-overall-architecture.md ... ADR-008-event-driven-modular-data-platform.md
│
├── contracts/                          # 3. CONTRACTS: Canonical interfaces, schemas & data governance
│   ├── README.md
│   ├── requirements-matrix.md
│   ├── api-contracts.md
│   ├── event-schemas.md
│   └── data-lineage.md
│
├── diagrams/                           # 4. DIAGRAMS: Single-source-of-truth Mermaid diagrams (22 diagrams)
│   ├── README.md
│   ├── system/ (DIAG-CTX-001, DIAG-C4-002, DIAG-C4-003)
│   ├── data-platform/ (DIAG-DATA-004..009)
│   ├── backend/ (DIAG-COMP-008..011, DIAG-SEQ-009)
│   ├── agent/ (DIAG-COMP-012, DIAG-SEQ-013, DIAG-COMP-014)
│   ├── deployment/ (DIAG-DEP-015, DIAG-DEP-018)
│   ├── security/ (DIAG-SEC-016)
│   ├── architecture/ (DIAG-C4-017, DIAG-C4-019)
│   └── ux/ (DIAG-UX-001)
│
├── operations/                         # 5. OPERATIONS: SRE, monitoring, deployment profiles & runbooks
│   ├── README.md
│   ├── deployment-guide.md
│   ├── monitoring-and-observability.md
│   ├── operational-runbooks.md
│   └── disaster-recovery.md
│
├── development/                        # 6. DEVELOPMENT: Developer setup, codebase map, tests & workflow
│   ├── README.md
│   ├── developer-quickstart.md
│   ├── codebase-map.md
│   ├── testing-guide.md
│   └── contribution-workflow.md
│
├── product/                            # 7. PRODUCT LIFECYCLE: Formal 15-phase records (00..14)
│   ├── README.md
│   ├── 00-discovery/ ... 14-governance/
│   └── features/
│
├── templates/                          # 8. TEMPLATES: Standardized document blueprints (14 categories)
│   ├── README.md
│   └── [14 categories of *.template.md]
│
└── archive/                            # 9. ARCHIVE: Preserved historical baseline snapshots & notes
    ├── README.md
    └── historical-notes.md
```

---

## 2. Reader Journey Mapping

Every developer and stakeholder can navigate directly to their point of interest within 2 clicks:

| Role / Persona | Reader Question | Target Destination | Authoritative Source |
|---|---|---|---|
| **New Developer** | *"How do I understand the system, clone the repo, and start running code in 5 minutes?"* | [docs/overview/](file:///c:/Users/PC/Project/FinancialMarketDataPlatform/docs/overview/) & [docs/development/](file:///c:/Users/PC/Project/FinancialMarketDataPlatform/docs/development/) | `developer-quickstart.md`, `codebase-map.md` |
| **System Architect** | *"What are the core architectural boundaries, design decisions, and system decomposition?"* | [docs/architecture/](file:///c:/Users/PC/Project/FinancialMarketDataPlatform/docs/architecture/) & [ADRs](file:///c:/Users/PC/Project/FinancialMarketDataPlatform/docs/architecture/adr/) | `00-architecture-overview.md`, `ADR-001..008` |
| **Data Engineer** | *"What are the Kafka topics, lakehouse partitioning, quality gates, and lineage paths?"* | [docs/contracts/](file:///c:/Users/PC/Project/FinancialMarketDataPlatform/docs/contracts/) & [docs/diagrams/data-platform/](file:///c:/Users/PC/Project/FinancialMarketDataPlatform/docs/diagrams/data-platform/) | `data-contracts.md`, `datasets.yaml`, `topics.yaml` |
| **API / Frontend Dev** | *"What endpoints, schemas, WebSocket channels, and SSE feeds are available?"* | [docs/contracts/api-contracts.md](file:///c:/Users/PC/Project/FinancialMarketDataPlatform/docs/contracts/api-contracts.md) | `api-specification.md`, `models/api/api.yaml` |
| **Site Reliability / DevOps** | *"How do I deploy microservices, monitor SLIs, inspect Prometheus alerts, and run recovery?"* | [docs/operations/](file:///c:/Users/PC/Project/FinancialMarketDataPlatform/docs/operations/) | `deployment-guide.md`, `monitoring.md`, `runbooks.md` |
| **AI Agent / Auditor** | *"What are the canonical rules, model contracts, and validation requirements for this task?"* | `AGENTS.md`, `.agents/`, `tools/validators/` | `document-map.yaml`, `identifier-registry.yaml` |

---

## 3. Structural Guarantees & Non-Duplication Policy

1. **Zero Content Drift**: Authoritative specifications (`docs/architecture/`, `docs/specifications/`, `models/`) remain the single source of truth. The new portals (`overview/`, `contracts/`, `operations/`, `development/`) provide synthesized, highly readable entrypoints linking to the canonical sources rather than duplicating raw text.
2. **100% Validator Compliance**: Every new directory contains a complete 12-section `README.md` satisfying `tools/validators/validate_readmes.py`.
3. **Preserved Baselined Files**: All 25 baseline files required by `tools/validators/validate_docs.py` remain intact at their designated paths.
4. **Stable Identifiers**: All identifiers (`ADR-*`, `FR-*`, `DIAG-*`, `COMP-*`, etc.) remain unaltered.

