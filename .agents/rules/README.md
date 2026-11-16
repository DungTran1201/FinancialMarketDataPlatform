# Agent Operating Rules (`.agents/rules/`)

## 1. Directory Purpose

Defines the 22 operational Agent rules (`RULE-001..010` and `DATA-RULE-001..012`) governing AI Agent behavior and data-platform engineering invariants across `FinancialMarketDataPlatform`.

## 2. Authority & Precedence

- Normative documentation standards, schemas, applicability rules, and lifecycle policies live in `docs/governance/` and `AGENTS.md`.
- `.agents/rules/` defines operational guardrails for Agents executing tasks; rules MUST NOT contradict `AGENTS.md` or `docs/governance/`.

## 3. Agent Role and Responsibilities

Maintained by `documentation-architect` and audited by `documentation-auditor` and `financial-data-platform-reviewer`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating contract and mandatory reading order.
2. `docs/governance/README.md` — Normative policies, standards, catalog, and schemas.
3. `.agents/config/` — Operational V2 mappings (`document-map.yaml`, `data-platform-boundaries.yaml`, `phase-gates.yaml`, `status-lifecycle.yaml`).

## 5. Active Rules Register (22 Rules)

| File | Rule ID | Purpose |
|---|---|---|
| `core.md` | `RULE-001` | Core Operating, Discovery Chain & Evidence Discipline |
| `documentation.md` | `RULE-002` | Documentation V2 Scope, Templates & Frontmatter Rule |
| `models.md` | `RULE-003` | Capability Manifests, Contracts & Schema Rule |
| `diagrams.md` | `RULE-004` | Scoped Diagram Governance & Derived View Rule |
| `traceability.md` | `RULE-005` | Bidirectional Traceability & Impact Analysis Rule |
| `identifiers.md` | `RULE-006` | Identifier Allocation & Preservation Rule |
| `source-of-truth.md` | `RULE-007` | Single Source-of-Truth & Conflict Resolution Rule |
| `change-lifecycle.md` | `RULE-008` | Documentation V2 Change Lifecycle & PR Rule |
| `security.md` | `RULE-009` | Security, Secret Isolation & Agent Safety Rule |
| `quality-gates.md` | `RULE-010` | Lifecycle Quality Gates & Status Promotion Rule |
| `data-truth-classification.md` | `DATA-RULE-001` | Data Platform Evidence & Implementation-State Classification Rule |
| `financial-data-correctness.md` | `DATA-RULE-002` | Financial Data Precision, Time & Identity Rule |
| `event-contract-evolution.md` | `DATA-RULE-003` | Kafka Event Contract & Schema Evolution Rule |
| `ingestion-reliability.md` | `DATA-RULE-004` | Exchange Ingestion Resilience & Watermark Rule |
| `kafka-consumer-delivery.md` | `DATA-RULE-005` | Kafka Consumer Delivery, Offset & DLQ Rule |
| `medallion-layer-ownership.md` | `DATA-RULE-006` | Lakehouse Medallion Layer Ownership Rule |
| `analytical-modeling.md` | `DATA-RULE-007` | ClickHouse & dbt Analytical Modeling Rule |
| `data-quality-gates.md` | `DATA-RULE-008` | Financial Data Quality Gate Enforcement Rule |
| `data-lineage-governance.md` | `DATA-RULE-009` | Data Lineage, Retention & Governance Rule |
| `data-platform-observability.md` | `DATA-RULE-010` | Data Platform Telemetry & Freshness Observability Rule |
| `data-platform-security-operations.md` | `DATA-RULE-011` | Data Platform Secret, Access & Plane Isolation Rule |
| `storage-workload-separation.md` | `DATA-RULE-012` | Polyglot Storage & OLTP/OLAP Workload Separation Rule |

## 6. Validation Commands

```powershell
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

## 7. Agent Restrictions

- Do NOT introduce application-specific persona/cosmetic rules from external projects.
- Do NOT weaken security, evidence classification, or `docs/governance/` source-of-truth precedence.
