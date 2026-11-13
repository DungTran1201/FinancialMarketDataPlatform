# Agent Engineering Skills Catalog (`.agents/skills/`)

## 1. Directory Purpose

Contains the 25 modular, discipline-specific Agent skill packages (`SKILL.md`) registered in `.agents/skill-registry.yaml` and `.agents/skills_manifest.json`.

## 2. Scope and Boundaries

- **Belongs in this directory**: 25 skill subdirectories, each containing an operational `README.md` and `SKILL.md`.
- **Does NOT belong in this directory**: Product-specific companion/avatar skills or application source code (`src/`).

## 3. Agent Role and Responsibilities

Used by all Agent roles in `.agents/agents/`; maintained by `documentation-architect`.

## 4. Authoritative Inputs

1. `.agents/skill-registry.yaml` — Active skill list.
2. `.agents/skills_manifest.json` — Skill metadata mapping.
3. `.agents/config/document-map.yaml` — Phase and template mapping.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `project-discovery/SKILL.md` | Project & Current-State Discovery | Required | `.agents/skills/project-discovery/README.md` |
| `documentation-creation/SKILL.md` | Template-Governed Documentation Authoring | Required | `.agents/skills/documentation-creation/README.md` |
| `requirements-engineering/SKILL.md` | Requirements Engineering & Normalization | Required | `.agents/skills/requirements-engineering/README.md` |
| `srs-generation/SKILL.md` | IEEE-Compatible SRS Generation | Required | `.agents/skills/srs-generation/README.md` |
| `architecture-modeling/SKILL.md` | System, Data & Software Architecture Modeling | Required | `.agents/skills/architecture-modeling/README.md` |
| `process-modeling/SKILL.md` | Business Process, BPMN & Swimlane Modeling | Required | `.agents/skills/process-modeling/README.md` |
| `use-case-modeling/SKILL.md` | Use Case Catalog & Specification Modeling | Required | `.agents/skills/use-case-modeling/README.md` |
| `domain-modeling/SKILL.md` | DDD Domain, Entity & Aggregate Modeling | Required | `.agents/skills/domain-modeling/README.md` |
| `api-contract/SKILL.md` | API & Event Contract Specification | Required | `.agents/skills/api-contract/README.md` |
| `diagram-modeling/SKILL.md` | Technical Diagram Authoring & Synchronization | Required | `.agents/skills/diagram-modeling/README.md` |
| `ux-modeling/SKILL.md` | UX Information Architecture & Screen Modeling | Required | `.agents/skills/ux-modeling/README.md` |
| `security-threat-modeling/SKILL.md` | STRIDE Threat Modeling & Security Control Design | Required | `.agents/skills/security-threat-modeling/README.md` |
| `test-modeling/SKILL.md` | Test Strategy, Test Plan & Test Case Modeling | Required | `.agents/skills/test-modeling/README.md` |
| `documentation-review/SKILL.md` | Documentation Quality & Gate Audit | Required | `.agents/skills/documentation-review/README.md` |
| `traceability-audit/SKILL.md` | Bidirectional Traceability Audit | Required | `.agents/skills/traceability-audit/README.md` |
| `documentation-validation/SKILL.md` | Automated Documentation & Model Validation | Required | `.agents/skills/documentation-validation/README.md` |
| `data-platform-discovery/SKILL.md` | Data Platform Current/Target Discovery & Gap Analysis | Required | `.agents/skills/data-platform-discovery/README.md` |
| `financial-market-data-ingestion/SKILL.md` | Exchange REST/WebSocket Ingestion & Normalization | Required | `.agents/skills/financial-market-data-ingestion/README.md` |
| `kafka-event-streaming/SKILL.md` | Kafka Event Contract, Partitioning & Consumer Safety | Required | `.agents/skills/kafka-event-streaming/README.md` |
| `lakehouse-medallion/SKILL.md` | MinIO/S3, Parquet & Iceberg Medallion Engineering | Required | `.agents/skills/lakehouse-medallion/README.md` |
| `analytics-engineering-dbt-clickhouse/SKILL.md` | ClickHouse OLAP & dbt Gold Mart Engineering | Required | `.agents/skills/analytics-engineering-dbt-clickhouse/README.md` |
| `financial-data-quality/SKILL.md` | Financial Data Quality Controls & Reconciliation | Required | `.agents/skills/financial-data-quality/README.md` |
| `data-governance-lineage/SKILL.md` | Dataset Ownership, Lineage, Retention & Provenance | Required | `.agents/skills/data-governance-lineage/README.md` |
| `dataops-observability/SKILL.md` | Streaming/Batch Telemetry, Freshness SLAs & Runbooks | Required | `.agents/skills/dataops-observability/README.md` |
| `data-platform-testing-recovery/SKILL.md` | Pipeline Replay, Backfill & Fault Recovery Verification | Required | `.agents/skills/data-platform-testing-recovery/README.md` |

## 6. Directory and File Organization

25 subdirectories (`project-discovery/` through `data-platform-testing-recovery/`), each containing `README.md` and `SKILL.md`.

## 7. Document Creation Rules

Every `SKILL.md` must include YAML frontmatter (`name`, `description`) and sections for Trigger Conditions, Inputs, Preconditions, Execution Procedure, Output Artifacts, Validation, Failure Handling, Restrictions, and Related Skills.

## 8. Creation Workflow

1. Read `.agents/skills/README.md` and the target skill directory's `README.md`.
2. Ensure the skill's inputs, templates, and outputs match `.agents/config/document-map.yaml`.
3. Register the skill in `.agents/skill-registry.yaml` and `.agents/skills_manifest.json`.
4. Validate via `tools/validators/validate_agent_config.py`.

## 9. Relationships and Dependencies

Invoked by Agent roles in `.agents/agents/` to produce models in `models/`, documents in `docs/`, and diagrams in `docs/diagrams/`.

## 10. Quality Gate

All 25 skill folders contain both `README.md` and `SKILL.md` and pass `validate_agent_config.py` and `validate_readmes.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT combine all engineering disciplines into a single monolithic skill.
- Do NOT copy unrelated skills (VRM, Discord, ponytail) from external repositories.
