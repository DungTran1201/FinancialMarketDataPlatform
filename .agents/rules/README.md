# Agent Operating Rules (`.agents/rules/`)

## 1. Directory Purpose

Defines the 22 mandatory, non-contradictory behavioral rules (`RULE-001..010` and `DATA-RULE-001..012`) governing all AI Agents and human contributors across the repository.

## 2. Scope and Boundaries

- **Belongs in this directory**: Concise, enforceable rule specifications (`*.md`) covering core behavior, documentation, models, diagrams, traceability, identifiers, source-of-truth, change lifecycle, security, and quality gates.
- **Does NOT belong in this directory**: Role definitions (`.agents/agents/`), step-by-step skill procedures (`.agents/skills/`), or product requirements (`docs/`).

## 3. Agent Role and Responsibilities

Maintained by `documentation-architect` and enforced by `documentation-auditor` and `tools/validators/`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root operating contract.
2. `.agents/config/` — Machine-readable governance registries.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `core.md` | Core Operating & README-First Rule | Required | `.agents/rules/README.md` |
| `documentation.md` | Documentation Authoring & Template Governance Rule | Required | `.agents/rules/README.md` |
| `models.md` | Canonical Model Governance Rule | Required | `.agents/rules/README.md` |
| `diagrams.md` | Diagram Governance & Derived View Rule | Required | `.agents/rules/README.md` |
| `traceability.md` | Bidirectional Traceability Rule | Required | `.agents/rules/README.md` |
| `identifiers.md` | Identifier Allocation & Preservation Rule | Required | `.agents/rules/README.md` |
| `source-of-truth.md` | Source-of-Truth Hierarchy & Conflict Resolution Rule | Required | `.agents/rules/README.md` |
| `change-lifecycle.md` | Work-Item Change Lifecycle Rule | Required | `.agents/rules/README.md` |
| `security.md` | Security, Secret Isolation & Agent Safety Rule | Required | `.agents/rules/README.md` |
| `quality-gates.md` | Phase Quality Gates & Status Promotion Rule | Required | `.agents/rules/README.md` |
| `data-truth-classification.md` | Data Platform Truth & Evidence Classification Rule (`DATA-RULE-001`) | Required | `.agents/rules/README.md` |
| `financial-data-correctness.md` | Financial Data Precision, Time & Identity Rule (`DATA-RULE-002`) | Required | `.agents/rules/README.md` |
| `event-contract-evolution.md` | Kafka Event Contract & Schema Evolution Rule (`DATA-RULE-003`) | Required | `.agents/rules/README.md` |
| `ingestion-reliability.md` | Exchange Ingestion Resilience & Watermark Rule (`DATA-RULE-004`) | Required | `.agents/rules/README.md` |
| `kafka-consumer-delivery.md` | Kafka Consumer Delivery, Offset & DLQ Rule (`DATA-RULE-005`) | Required | `.agents/rules/README.md` |
| `medallion-layer-ownership.md` | Lakehouse Medallion Layer Ownership Rule (`DATA-RULE-006`) | Required | `.agents/rules/README.md` |
| `analytical-modeling.md` | ClickHouse & dbt Analytical Modeling Rule (`DATA-RULE-007`) | Required | `.agents/rules/README.md` |
| `data-quality-gates.md` | Financial Data Quality Gate Enforcement Rule (`DATA-RULE-008`) | Required | `.agents/rules/README.md` |
| `data-lineage-governance.md` | Data Lineage, Retention & Governance Rule (`DATA-RULE-009`) | Required | `.agents/rules/README.md` |
| `data-platform-observability.md` | Data Platform Telemetry & Freshness Observability Rule (`DATA-RULE-010`) | Required | `.agents/rules/README.md` |
| `data-platform-security-operations.md` | Data Platform Secret, Access & Plane Isolation Rule (`DATA-RULE-011`) | Required | `.agents/rules/README.md` |
| `storage-workload-separation.md` | Polyglot Storage & OLTP/OLAP Workload Separation Rule (`DATA-RULE-012`) | Required | `.agents/rules/README.md` |

## 6. Directory and File Organization

Flat directory containing `README.md` and 22 `<rule-slug>.md` files.

## 7. Document Creation Rules

Every rule file must include `Rule ID`, `Trigger Scope`, `Mandatory Directives`, `Prohibited Actions`, and `Verification Mechanism`.

## 8. Creation Workflow

1. Read `.agents/rules/README.md` and `AGENTS.md`.
2. Ensure any new or updated rule does not conflict with existing rules.
3. Verify rule enforcement coverage in `tools/validators/`.
4. Run `tools/validators/validate_agent_config.py`.

## 9. Relationships and Dependencies

Referenced by all Agent roles in `.agents/agents/` and enforced by `tools/validators/` and `tools/hooks/`.

## 10. Quality Gate

All 22 rule files exist, have unique `RULE-###` or `DATA-RULE-###` IDs, and pass `validate_agent_config.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT introduce application-specific persona/cosmetic rules (such as AI-Chan `ponytail.md`).
- Do NOT weaken security or source-of-truth precedence in any rule.
