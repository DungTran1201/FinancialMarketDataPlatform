# Documentation Archive Domain (`docs/archive/`)

## 1. Directory Purpose

`docs/archive/` serves as the historical preservation and superseded artifact repository for the **FinancialMarketDataPlatform**. It preserves historical architecture drafts, migration retrospectives, baseline snapshots, and superseded technical records without cluttering the active engineering portals.

## 2. Scope and Boundaries

- **Belongs in `docs/archive/`**:
  - Historical architecture evolution notes.
  - Superseded design proposals and retrospective reports.
  - Historical snapshots kept for audit and backward reference.
- **Does NOT belong in `docs/archive/`**:
  - Active architecture baselines (which live in `docs/architecture/`).
  - Active specifications or canonical contracts (which live in `docs/contracts/` or `models/`).
  - Active operational runbooks (which live in `docs/operations/`).

## 3. Agent Role and Responsibilities

- **Primary Owning Role**: `documentation-architect`.
- **Collaborating Roles**: `documentation-auditor`.
- **Responsibilities**:
  - Preserve historical engineering context without allowing obsolete designs to masquerade as active architectures.
  - Clearly tag archived documents with status `SUPERSEDED` or `ARCHIVED`.

## 4. Authoritative Inputs

1. [work-items/ARCH-001-event-driven-modular-restructure/](../../work-items/ARCH-001-event-driven-modular-restructure/) — Architecture Restructuring Work Item.
2. [work-items/DATA-001-data-platform-v01-and-microservices/](../../work-items/DATA-001-data-platform-v01-and-microservices/) — Data Platform v0.1 Work Item.
3. [docs/architecture/adr/ADR-007-microservices-and-data-platform-v01.md](../architecture/adr/ADR-007-microservices-and-data-platform-v01.md) — Microservices ADR.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Domain scope, boundaries, and navigation index | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `historical-notes.md` | Architecture evolution records and migration history | Required | `docs/templates/architecture/architecture-overview.template.md` |

## 6. Directory and File Organization

```text
docs/archive/
├── README.md           # Domain overview & 12-section contract
└── historical-notes.md # Architecture evolution and superseded designs
```

## 7. Document Creation Rules

- Every archived document must carry a clear header indicating `SUPERSEDED` or `ARCHIVED` status.
- Every archived document must cross-reference the active replacement document.

## 8. Creation Workflow

1. Identify superseded design or historical snapshot.
2. Add migration notes and link to the active canonical document.
3. Validate links and run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

- **Upstream**: Superseded artifacts from `docs/architecture/` and earlier work items.
- **Downstream**: Referenced as historical background by ADRs and audit reports.

## 10. Quality Gate

- All documents carry clear `SUPERSEDED` status headers.
- Zero broken links.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- **Do NOT** cite documents in this directory as authoritative sources of current implementation behavior.
- **Do NOT** delete archived files.
