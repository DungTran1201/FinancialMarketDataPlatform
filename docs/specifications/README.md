# Shared Platform Specifications (`docs/specifications/`)

## 1. Directory Purpose

Stores the baselined shared platform specifications covering Data Requirements (`FR-01..10`), Canonical Data Dictionary, Kafka Event Data Contracts, REST/WS/SSE API Specification, and Non-Functional Requirements (`NFR`).

## 2. Scope and Boundaries

- **Belongs in this directory**: `data-requirements.md`, `data-dictionary.md`, `data-contracts.md`, `api-specification.md`, and `non-functional-requirements.md`.
- **Does NOT belong in this directory**: Website-only feature SRS (`docs/product/02-requirements/`) or canonical YAML files (`models/`).

## 3. Agent Role and Responsibilities

Maintained by `requirements-engineer`, `domain-modeler`, and `api-architect`.

## 4. Authoritative Inputs

1. `models/requirements/requirements.yaml`
2. `models/domain/entities.yaml`
3. `models/api/api.yaml` and `models/api/integrations.yaml`

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `data-requirements.md` | Functional & data ingestion requirements (`FR-01..10`) | Required | `docs/templates/requirements/functional-requirements.template.md` |
| `data-dictionary.md` | Canonical entities & precision across Redis, ClickHouse, Iceberg, PG | Required | `docs/templates/domain/entity.template.md` |
| `data-contracts.md` | Kafka topic topology & `EventEnvelopeV1` JSON schemas | Required | `docs/templates/api/integration-contract.template.md` |
| `api-specification.md` | Versioned `/api/v1` and `/ws/v1` endpoint contracts | Required | `docs/templates/api/API-specification.template.md` |
| `non-functional-requirements.md` | P50/P95/P99 latency targets, resilience matrix & benchmarks | Required | `docs/templates/requirements/non-functional-requirements.template.md` |

## 6. Directory and File Organization

Flat directory `docs/specifications/` containing 5 core platform specification documents plus `README.md`.

## 7. Document Creation Rules

All 5 existing files are `BASELINED`. Updates require a `DATA`, `API`, or `ARCH` work item and synchronization with `models/`.

## 8. Creation Workflow

1. Read `docs/specifications/README.md`.
2. Update the corresponding YAML model in `models/` (`requirements`, `domain`, or `api`).
3. Update the specification file preserving existing IDs (`FR-01..10`).
4. Run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

Serves as the shared data and API foundation for `docs/product/` and `docs/features/`.

## 10. Quality Gate

All 5 specification files remain synchronized with `models/` and pass `validate_docs.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT overwrite or delete the 5 baselined specification files without a work item.
- Do NOT replace exact `Decimal(38,18)` financial rules with floating-point types.
