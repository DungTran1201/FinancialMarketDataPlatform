# Agent Engineering Skills Catalog (`.agents/skills/`)

## 1. Directory Purpose

Contains the 25 modular, discipline-specific Agent skill packages (`SKILL.md` + `README.md`) registered in `.agents/skill-registry.yaml` and `.agents/skills_manifest.json` and aligned to **Documentation V2**.

## 2. Scope and Boundaries

- **Belongs in this directory**: 25 skill subdirectories, each containing an operational `README.md` and `SKILL.md`.
- **Does NOT belong in this directory**: Product-specific companion/avatar skills or application source code (`src/`).

## 3. Agent Role and Responsibilities

Used by all 19 Agent roles in `.agents/agents/`; maintained by `documentation-architect` and audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `.agents/skill-registry.yaml` — Active skill list.
2. `.agents/skills_manifest.json` — Skill metadata mapping.
3. `.agents/config/document-map.yaml` — Documentation V2 Plane/Domain/Capability and template mapping.
4. `docs/governance/documentation-lifecycle.md` — 9-stage Documentation V2 lifecycle.

## 5. Active Skills (25 Packages)

| Skill | Purpose | Owner Role |
|---|---|---|
| `project-discovery/SKILL.md` | Current-State Discovery & Impact Analysis | `discovery-analyst` |
| `documentation-creation/SKILL.md` | Template-Governed Documentation V2 Authoring | `documentation-architect` |
| `requirements-engineering/SKILL.md` | Capability Requirements, Business Rules & NFR Engineering | `requirements-engineer` |
| `srs-generation/SKILL.md` | Capability Specification & Requirements Synthesis | `requirements-engineer` |
| `architecture-modeling/SKILL.md` | Plane/Capability Architecture, C4 & MADR 4.0 ADRs | `architecture-modeler` |
| `process-modeling/SKILL.md` | Cross-Actor Workflow & BPMN/Swimlane Modeling | `process-modeler` |
| `use-case-modeling/SKILL.md` | Capability Use Case Modeling | `requirements-engineer` |
| `domain-modeling/SKILL.md` | Domain Boundaries, Data Models, DB Design & ERDs | `domain-modeler` |
| `api-contract/SKILL.md` | OpenAPI 3.1, AsyncAPI 3.1, Data Contracts & Error Catalogs | `api-architect` |
| `diagram-modeling/SKILL.md` | Scoped Derived Mermaid Diagram Authoring | `architecture-modeler` |
| `ux-modeling/SKILL.md` | Frontend Architecture, Compatibility & Screen Flows | `ux-modeler` |
| `security-threat-modeling/SKILL.md` | Threat Modeling, Security Controls & AuthZ Matrices | `security-reviewer` |
| `test-modeling/SKILL.md` | Plane Test Plans, Scenarios & Deterministic Test Cases | `qa-reviewer` |
| `documentation-review/SKILL.md` | Documentation V2 Quality & Gate Audit (`QG-1..QG-7`) | `documentation-auditor` |
| `traceability-audit/SKILL.md` | Bidirectional Capability Traceability Audit | `documentation-auditor` |
| `documentation-validation/SKILL.md` | Automated Documentation V2 Validation | `documentation-auditor` |
| `data-platform-discovery/SKILL.md` | Data Platform `AS-IS` vs `TARGET` Discovery & Gap Analysis | `data-platform-architect` |
| `financial-market-data-ingestion/SKILL.md` | Exchange REST/WebSocket Ingestion & Normalization | `streaming-data-engineer` |
| `kafka-event-streaming/SKILL.md` | Kafka Event Contract, Partitioning & Consumer Safety | `streaming-data-engineer` |
| `lakehouse-medallion/SKILL.md` | MinIO/S3, Parquet & Iceberg Medallion Engineering | `lakehouse-engineer` |
| `analytics-engineering-dbt-clickhouse/SKILL.md` | ClickHouse OLAP & dbt Gold Mart Engineering | `analytics-engineer` |
| `financial-data-quality/SKILL.md` | Financial Data Quality Controls & Reconciliation | `data-quality-governance-engineer` |
| `data-governance-lineage/SKILL.md` | Dataset Ownership, Lineage, Retention & Provenance | `data-quality-governance-engineer` |
| `dataops-observability/SKILL.md` | Streaming/Batch Telemetry, Freshness SLOs & Runbooks | `dataops-engineer` |
| `data-platform-testing-recovery/SKILL.md` | Pipeline Replay, Backfill & Fault Recovery Verification | `financial-data-platform-reviewer` |

## 6. Document Creation Rules

Every `SKILL.md` must include YAML frontmatter (`name`, `description`) and sections for Description, Trigger Conditions, Authoritative Inputs, Preconditions, Execution Procedure, Output Artifacts, Validation, Failure Handling, Restrictions, and Related Skills.

## 7. Validation Commands

```powershell
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 8. Agent Restrictions

- Do NOT combine all engineering disciplines into a single monolithic skill.
- Do NOT copy unrelated skills from external repositories without `.agents/catalog/external-skill-policy.md` quarantine review.
