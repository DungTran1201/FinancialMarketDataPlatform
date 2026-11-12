# Platform Architecture Decision Records (`docs/architecture/adr/`)

## 1. Directory Purpose

Stores the authoritative Architecture Decision Records (`ADR-001` through `ADR-006` and future platform ADRs) governing technology, storage, streaming, backend, caching, and Agent isolation trade-offs.

## 2. Scope and Boundaries

- **Belongs in this directory**: `ADR-001-overall-architecture.md` through `ADR-006-agent-integration.md` and future `ADR-NNN-*.md` files.
- **Does NOT belong in this directory**: Product-specific UI decisions (`docs/product/06-architecture/adr/`) or general prose specs.

## 3. Agent Role and Responsibilities

Authored by `architecture-modeler` and audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `models/architecture/architecture.yaml` — Canonical decisions list.
2. `docs/templates/architecture/ADR.template.md` — Standard 12-section ADR template.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `ADR-001-overall-architecture.md` | Three-Plane Streaming-First Hybrid Lakehouse | Required | `docs/templates/architecture/ADR.template.md` |
| `ADR-002-event-driven-data-platform.md` | Kafka Event Backbone & Streaming vs. Batch Boundaries | Required | `docs/templates/architecture/ADR.template.md` |
| `ADR-003-storage-strategy.md` | Polyglot Storage Segregation (Redis, ClickHouse, Iceberg, PG) | Required | `docs/templates/architecture/ADR.template.md` |
| `ADR-004-backend-architecture.md` | FastAPI Modular Monolith, Hexagonal & Selective CQRS | Required | `docs/templates/architecture/ADR.template.md` |
| `ADR-005-query-and-caching-strategy.md` | Workload Query Routing, Lua Monotonic State & Fallback | Required | `docs/templates/architecture/ADR.template.md` |
| `ADR-006-agent-integration.md` | Isolated Intelligence Plane & Deterministic Tool Gateway | Required | `docs/templates/architecture/ADR.template.md` |

## 6. Directory and File Organization

Flat directory `docs/architecture/adr/` with files named `ADR-<NNN>-<kebab-slug>.md`.

## 7. Document Creation Rules

Every ADR must use `docs/templates/architecture/ADR.template.md`, allocate the next sequential `ADR-NNN` ID without renumbering existing ADRs, and register in `models/architecture/architecture.yaml`.

## 8. Creation Workflow

1. Read `docs/architecture/adr/README.md`.
2. Instantiate `docs/templates/architecture/ADR.template.md`.
3. Document context, problem, selected option, rejected alternatives, benefits, drawbacks, limitations, and invalidation conditions.
4. Register the ADR in `models/architecture/architecture.yaml`.
5. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Referenced by `docs/architecture/00..13`, `models/architecture/architecture.yaml`, and `src/`.

## 10. Quality Gate

All ADRs contain all mandatory decision sections and match `models/architecture/architecture.yaml`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT renumber or delete `ADR-001` through `ADR-006`.
- Do NOT introduce unapproved technologies without a ratified ADR.
