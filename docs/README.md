# Master Documentation System Index (`docs/`)

## 1. Directory Purpose

`docs/` is the authoritative human-readable specification and engineering documentation root for the **FinancialMarketDataPlatform**. It organizes the platform's technical documentation into **Engineering Domains & Reader Journeys** while preserving the canonical Data Platform & Backend baselines (`docs/architecture/`, `docs/specifications/`), unified technical diagrams (`docs/diagrams/`), operational runbooks (`docs/operations/`), developer onboarding guides (`docs/development/`), contracts portal (`docs/contracts/`), 15-phase product lifecycle records (`docs/product/`), template library (`docs/templates/`), and historical archives (`docs/archive/`).

## 2. Scope and Boundaries

- **Belongs in this directory**: `overview/`, `architecture/`, `contracts/`, `specifications/`, `diagrams/`, `operations/`, `development/`, `product/`, `features/`, `templates/`, and `archive/`.
- **Does NOT belong in this directory**: Machine-readable canonical YAML models (`models/`), change-control work items (`work-items/`), or Agent OS configurations (`.agents/`).

## 3. Agent Role and Responsibilities

- **Governing Role**: `documentation-architect` (Senior Documentation Architect).
- **Auditing Role**: `documentation-auditor`.
- **Responsibilities**:
  - Enforce domain boundaries and prevent content drift or parallel documentation roots.
  - Maintain 100% bidirectional traceability with `models/` and test suites.
  - Preserve all 25 baseline files and 22 technical diagrams.

## 4. Authoritative Inputs

1. [AGENTS.md](../AGENTS.md) — Root Agent operating system contract.
2. [.agents/config/document-map.yaml](../.agents/config/document-map.yaml) — Master directory and phase mapping.
3. [models/](../models/) — Canonical structured YAML models (38 files).

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `overview/` | Platform vision, 3-plane separation, and polyglot tech stack | Required | `docs/overview/README.md` |
| `architecture/` | Preserved architecture specifications (00..14) and ADRs (001..008) | Required | `docs/architecture/README.md` |
| `contracts/` | Traceability matrix, API contracts, WebSocket/SSE specs, Kafka schemas | Required | `docs/contracts/README.md` |
| `specifications/` | Preserved baseline data platform and API specifications | Required | `docs/specifications/README.md` |
| `diagrams/` | Unified technical diagram subsystem (`22` active `DIAG-*` diagrams + `12` diagram templates = `34` files) | Required | `docs/diagrams/README.md` |
| `operations/` | Production container deployment, SRE runbooks, and Prometheus alerts | Required | `docs/operations/README.md` |
| `development/` | 5-minute setup, local test execution, and architectural codebase map | Required | `docs/development/README.md` |
| `product/` | 15-phase Product & Website lifecycle documentation (`00`..`14`) | Required | `docs/product/README.md` |
| `features/` | Self-contained feature documentation packages | Conditional | `docs/features/README.md` |
| `templates/` | Centralized reusable document template library (14 categories) | Required | `docs/templates/README.md` |
| `archive/` | Historical architecture notes, superseded designs, and snapshots | Required | `docs/archive/README.md` |

## 6. Directory and File Organization

Divided into 11 clear top-level domain directories under `docs/` without duplicate documentation roots. Every directory maintains a standardized 12-section `README.md`.

## 7. Document Creation Rules

Every document must be instantiated from `docs/templates/`, carry a registered identifier from `.agents/config/identifier-registry.yaml`, maintain link integrity, and synchronize with `models/`.

## 8. Creation Workflow

1. Read `AGENTS.md` and this `docs/README.md`.
2. Navigate to the target domain portal (`docs/overview/`, `docs/contracts/`, `docs/operations/`, `docs/development/`, etc.) and read its `README.md`.
3. Consult and update the corresponding canonical YAML model in `models/` first.
4. Instantiate the required template from `docs/templates/`.
5. Execute validation suite `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

- **Upstream**: Derived from canonical models in `models/`.
- **Downstream**: Directs source code implementation in `src/`, `frontend/`, and `deploy/`, and verification in `tests/`.

## 10. Quality Gate

100% of managed subdirectories under `docs/` contain a valid 12-section `README.md` and pass `tools/validators/run_all.py` with 0 errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- **Do NOT** create parallel documentation roots outside `docs/`.
- **Do NOT** overwrite or delete existing baselined Data Platform architecture (`00..14`) or ADR files (`ADR-001..008`).
- **Do NOT** break existing links or renumber registered identifiers.
