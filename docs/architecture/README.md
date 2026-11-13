# Shared Platform Architecture Baseline (`docs/architecture/`)

## 1. Directory Purpose

Holds the baselined Phase 0 system, Data Platform, Modular Monolith Backend, and Agentic Intelligence architecture documents (`00` through `13`) and Architecture Decision Records (`adr/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: `00-architecture-overview.md` through `13-performance-and-scalability.md` and `adr/`.
- **Does NOT belong in this directory**: Website-only UX screen specs (`docs/product/11-ux/`) or raw YAML models (`models/architecture/`).

## 3. Agent Role and Responsibilities

Owned by `architecture-modeler` and reviewed by `documentation-architect` and `security-reviewer`.

## 4. Authoritative Inputs

1. `models/architecture/architecture.yaml` and `models/architecture/components.yaml`.
2. `docs/specifications/` — Shared data and API specifications.
3. `docs/templates/architecture/` — SAD, C4, and ADR templates.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `00-architecture-overview.md` | Executive three-plane blueprint & phased roadmap | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `01-system-context.md` | C4 Level 1 System Context & External Actor Boundaries | Required | `docs/templates/architecture/SAD.template.md` |
| `02-system-container-architecture.md` | C4 Level 2 Runtime Containers & Polyglot Storage | Required | `docs/templates/architecture/SAD.template.md` |
| `03-component-architecture.md` | C4 Level 3 Internal Module & Component Architecture | Required | `docs/templates/architecture/SAD.template.md` |
| `04-data-platform-architecture.md` | Plane A Ingestion, Kafka Streaming & Lakehouse Medallion Architecture | Required | `docs/templates/architecture/SAD.template.md` |
| `05-backend-architecture.md` | Plane B FastAPI Modular Monolith, CQRS & Hexagonal Architecture | Required | `docs/templates/architecture/SAD.template.md` |
| `06-agentic-intelligence-architecture.md` | Plane C LangGraph Orchestrator, Tool Gateway & Guardrail Architecture | Required | `docs/templates/architecture/SAD.template.md` |
| `07-data-storage-and-modeling.md` | Polyglot Storage & Schema Design (Iceberg, ClickHouse, PostgreSQL, Redis, Qdrant) | Required | `docs/templates/architecture/SAD.template.md` |
| `08-data-flow-and-event-contracts.md` | End-to-End Hot, Warm, Cold, Backfill & RAG Data Pipelines | Required | `docs/templates/architecture/SAD.template.md` |
| `09-api-and-integration-architecture.md` | REST, WebSocket, SSE & Kafka Event Integration Contracts | Required | `docs/templates/architecture/SAD.template.md` |
| `10-security-and-governance.md` | Security Trust Boundaries, Zero-Direct-DB Isolation & Data Governance | Required | `docs/templates/architecture/SAD.template.md` |
| `11-reliability-and-observability.md` | Fault Tolerance, Replayability, SLIs/SLOs & OpenTelemetry Observability | Required | `docs/templates/architecture/SAD.template.md` |
| `12-deployment-architecture.md` | Docker Compose Profiles, Local Developer Topology & Runtime Dependencies | Required | `docs/templates/architecture/SAD.template.md` |
| `13-performance-and-scalability.md` | Latency Budgets, Throughput Targets, Partitioning & Scaling Strategy | Required | `docs/templates/architecture/SAD.template.md` |
| `adr/` | Architecture Decision Records (`ADR-001`..`ADR-006`) | Required | `docs/architecture/adr/README.md` |

## 6. Directory and File Organization

Contains 14 numbered architecture documents (`00`..`13`) and the `adr/` subdirectory.

## 7. Document Creation Rules

All existing `00`..`13` files are `BASELINED`. Any modification requires an active `ARCH` work item, updated `models/architecture/`, and a new or updated ADR.

## 8. Creation Workflow

1. Read `docs/architecture/README.md`.
2. Inspect `models/architecture/architecture.yaml` and `components.yaml`.
3. Use `docs/templates/architecture/` for any new architectural extension.
4. Synchronize corresponding diagrams in `docs/diagrams/`.
5. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Provides the foundational platform constraints for `docs/product/06-architecture/` and `src/`.

## 10. Quality Gate

All 14 architecture documents and 6 ADRs are preserved intact and pass `validate_docs.py` and `validate_traceability.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT overwrite or delete existing `00`..`13` architecture files without an approved `ARCH` work item.
- Do NOT duplicate these platform architecture documents inside `docs/product/06-architecture/`.
