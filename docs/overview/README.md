# Platform Overview Domain (`docs/overview/`)

## 1. Directory Purpose

`docs/overview/` serves as the primary orientation and executive entrypoint for the **FinancialMarketDataPlatform**. It provides a high-level conceptual explanation of the system, its 3-plane separation, data lifecycle, core business value, and polyglot technology stack for engineers, architects, and stakeholders.

## 2. Scope and Boundaries

- **Belongs in `docs/overview/`**:
  - High-level system context and architectural mission summaries.
  - End-to-end data platform conceptual flows (`Exchange → Ingestion → Kafka → Redis / ClickHouse / Iceberg → Serving → UI / Agent`).
  - Consolidated technology stack specifications and architectural layer mappings.
- **Does NOT belong in `docs/overview/`**:
  - Detailed low-level class or module code specifications (see `docs/architecture/` and `src/`).
  - Raw API schema definitions or database DDLs (see `docs/contracts/` and `models/`).
  - Active change requests or gate records (see `work-items/`).

## 3. Agent Role and Responsibilities

- **Primary Owning Role**: `documentation-architect`.
- **Collaborating Roles**: `system-architect`, `data-platform-architect`.
- **Responsibilities**:
  - Maintain an intuitive, accessible overview of the entire platform.
  - Ensure conceptual consistency with authoritative models in `models/` and architecture ADRs in `docs/architecture/adr/`.

## 4. Authoritative Inputs

1. [docs/architecture/00-architecture-overview.md](../architecture/00-architecture-overview.md) — Baseline Architecture Overview.
2. [docs/architecture/01-system-context.md](../architecture/01-system-context.md) — Baseline System Context.
3. [docs/architecture/adr/ADR-001-overall-architecture.md](../architecture/adr/ADR-001-overall-architecture.md) — Modular Monolith & 3-Plane Architecture.
4. [docs/architecture/adr/ADR-008-event-driven-modular-data-platform.md](../architecture/adr/ADR-008-event-driven-modular-data-platform.md) — Event-Driven Modular Platform.
5. [models/architecture/architecture.yaml](../../models/architecture/architecture.yaml) — Canonical Architecture Model.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Directory scope, boundaries, and navigation index | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `system-overview.md` | Comprehensive platform vision, 3-plane framework, and end-to-end data flow | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `technology-stack.md` | Consolidated technology stack and storage layer responsibilities | Required | `docs/templates/architecture/architecture-overview.template.md` |

## 6. Directory and File Organization

```text
docs/overview/
├── README.md              # Domain overview & 12-section contract
├── system-overview.md     # Executive & engineering platform summary
└── technology-stack.md    # Technology choices, tools, and runtimes
```

## 7. Document Creation Rules

- Documents must link to canonical models in `models/` and baseline specifications in `docs/architecture/`.
- Fact classification must be maintained: Do not describe planned future capabilities as currently implemented.

## 8. Creation Workflow

1. Consult `docs/architecture/` and `models/architecture/`.
2. Author overview summaries with clear diagrams and tables.
3. Verify links and run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

- **Upstream**: Synthesizes inputs from `docs/architecture/` and `models/`.
- **Downstream**: Referenced by `docs/README.md`, `README.md`, and onboarding guides in `docs/development/`.

## 10. Quality Gate

- All documents contain valid metadata headers.
- All technical claims correspond to implemented or planned components documented in `documentation-migration-matrix.md`.
- Zero broken links.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- **Do NOT** duplicate deep API specs or full schemas in this directory.
- **Do NOT** mark unverified architectural designs as implemented.
