# Canonical Data Platform Models (`models/data-platform/`)

## 1. Directory Purpose

Contains the authoritative machine-readable YAML models governing the Event-Driven Data Platform (`Plane A`), covering canonical datasets, event schemas, Kafka topics, data quality gates, end-to-end lineage graphs, and polyglot storage retention policies.

## 2. Scope and Boundaries

- **Belongs in `models/data-platform/`**: `datasets.yaml`, `events.yaml`, `topics.yaml`, `quality-rules.yaml`, `lineage.yaml`, and `retention.yaml`.
- **Does NOT belong here**: Domain API endpoints (`models/api/`), serving bounded contexts (`models/domain/`), or security threat models (`models/security/`).

## 3. Agent Role and Responsibilities

- **Primary Owning Role**: `data-platform-architect` (`.agents/agents/data-platform-architect.md`).
- **Cooperating Roles**: `data-engineer` and `documentation-auditor`.

## 4. Authoritative Inputs

1. [docs/architecture/04-data-platform-architecture.md](../../docs/architecture/04-data-platform-architecture.md) — Core 12-stage Data Lifecycle specification.
2. [docs/architecture/14-data-platform-v01-and-microservices-architecture.md](../../docs/architecture/14-data-platform-v01-and-microservices-architecture.md) — Production Data Platform v0.1 implementation engines.
3. [docs/specifications/data-dictionary.md](../../docs/specifications/data-dictionary.md) — Canonical schemas and fixed-point precision standards.
4. `src/shared/contracts/`, `src/streaming/`, and `src/lakehouse/` — Verified implementation contracts.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `datasets.yaml` | Canonical dataset inventory across Raw, Bronze, Silver, Gold, Hot, and Control tiers (`MODEL-DP-001`) | Required | `models/data-platform/datasets.yaml` |
| `events.yaml` | Canonical `EventEnvelopeV1` and `DeadLetterEnvelopeV1` event contract specifications (`MODEL-DP-002`) | Required | `models/data-platform/events.yaml` |
| `topics.yaml` | Kafka topic partitioning, replication, consumer groups, and retention configuration (`MODEL-DP-003`) | Required | `models/data-platform/topics.yaml` |
| `quality-rules.yaml` | Blocking pre-Gold data quality expectations (`DQ-KLINE-*`, `DQ-TRADE-*`) (`MODEL-DP-004`) | Required | `models/data-platform/quality-rules.yaml` |
| `lineage.yaml` | End-to-end directed dataset lineage graph (`Stage 1 -> Stage 12`) (`MODEL-DP-005`) | Required | `models/data-platform/lineage.yaml` |
| `retention.yaml` | Polyglot storage retention, compaction, and TTL policies (`MODEL-DP-006`) | Required | `models/data-platform/retention.yaml` |

## 6. Directory and File Organization

Flat directory `models/data-platform/` containing `README.md` and the 6 canonical `.yaml` Data Platform governance models.

## 7. Document Creation Rules

- Every YAML file must include `version: "1.0"`, a valid 9-key `metadata` block with unique `model_id`, and verified `source_documents` paths.
- Keep natural keys, topic names, consumer groups, and DQ rule IDs synchronized with `src/shared/contracts/`, `src/streaming/`, `src/lakehouse/`, and `deploy/`.

## 8. Creation Workflow

1. Read `models/data-platform/README.md` and inspect `src/shared/contracts/` and `src/lakehouse/`.
2. Update canonical YAML models prior to updating derived documentation or Mermaid diagrams (`DIAG-DATA-*`).
3. Verify with `tools/validators/validate_models.py` and `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

- Upstream specifications: `docs/architecture/04-data-platform-architecture.md`, `docs/architecture/14-data-platform-v01-and-microservices-architecture.md`, and `docs/specifications/data-dictionary.md`.
- Downstream synchronized artifacts: `deploy/kafka/topics-init.sh`, `deploy/iceberg/catalog-config.yaml`, `docs/diagrams/data-platform/`, and `tests/contract/`.

## 10. Quality Gate

- Passes `validate_models.py`, `validate_readmes.py`, `validate_identifiers.py`, and `tests/contract/test_topic_and_dataset_contracts.py` with 0 errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_models.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- **Do NOT** invent datasets, Kafka topics, or quality rules not backed by code or approved ADRs.
- **Do NOT** violate `storage-workload-separation.md` (`ADR-003`) by merging OLTP, OLAP, hot cache, or lakehouse ownership.

