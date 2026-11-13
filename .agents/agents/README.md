# Agent Role Definitions (`.agents/agents/`)

## 1. Directory Purpose

Defines the 19 specialized AI Agent roles that collaborate across the documentation, product, and financial data platform engineering lifecycle.

## 2. Scope and Boundaries

- **Belongs in this directory**: Markdown role specifications (`*.md`) defining Agent ID, mission, allowed directories, prohibited actions, inputs, outputs, required skills, and handoff rules.
- **Does NOT belong in this directory**: Executable Python scripts (`tools/`), reusable skill steps (`.agents/skills/`), or global rules (`.agents/rules/`).

## 3. Agent Role and Responsibilities

Managed by `documentation-architect` and audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating protocol.
2. `.agents/skill-registry.yaml` — Active skills catalog.
3. `.agents/config/phase-gates.yaml` — Gate ownership mapping.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `documentation-architect.md` | Principal Documentation Architect | Required | `.agents/agents/README.md` |
| `discovery-analyst.md` | Discovery & Impact Analyst | Required | `.agents/agents/README.md` |
| `requirements-engineer.md` | Requirements & Use Case Engineer | Required | `.agents/agents/README.md` |
| `process-modeler.md` | Business Process Modeler | Required | `.agents/agents/README.md` |
| `architecture-modeler.md` | System, Data & Software Architecture Modeler | Required | `.agents/agents/README.md` |
| `domain-modeler.md` | DDD Domain & Data Modeler | Required | `.agents/agents/README.md` |
| `api-architect.md` | API & Integration Contract Architect | Required | `.agents/agents/README.md` |
| `ux-modeler.md` | UX & Information Architecture Modeler | Required | `.agents/agents/README.md` |
| `security-reviewer.md` | Security & Governance Reviewer | Required | `.agents/agents/README.md` |
| `qa-reviewer.md` | QA & Verification Architect | Required | `.agents/agents/README.md` |
| `documentation-auditor.md` | Documentation Governance & Quality Auditor | Required | `.agents/agents/README.md` |
| `data-platform-architect.md` | Financial Data Platform Architect | Required | `.agents/agents/README.md` |
| `data-engineer.md` | Market Data Ingestion & Pipeline Engineer | Required | `.agents/agents/README.md` |
| `streaming-data-engineer.md` | Kafka Event Streaming & Consumer Engineer | Required | `.agents/agents/README.md` |
| `lakehouse-engineer.md` | Lakehouse Medallion & Iceberg Engineer | Required | `.agents/agents/README.md` |
| `analytics-engineer.md` | ClickHouse & dbt Analytics Engineer | Required | `.agents/agents/README.md` |
| `data-quality-governance-engineer.md` | Financial Data Quality & Governance Engineer | Required | `.agents/agents/README.md` |
| `dataops-engineer.md` | DataOps, Observability & Recovery Engineer | Required | `.agents/agents/README.md` |
| `financial-data-platform-reviewer.md` | Financial Data Platform Principal Reviewer | Required | `.agents/agents/README.md` |

## 6. Directory and File Organization

Flat directory containing `README.md` and 19 `<role-slug>.md` files.

## 7. Document Creation Rules

Every role file must define: Metadata table (`Agent ID`, `Role Name`, `Status`), Mission, Responsibilities, Allowed Directories, Prohibited Actions, Authoritative Inputs, Expected Outputs, Required Skills, Required Rules, Handoff Conditions, and Quality Criteria.

## 8. Creation Workflow

1. Read `.agents/agents/README.md`.
2. Verify that the role has a distinct responsibility not already covered by an existing Agent.
3. Map the role to existing skills in `.agents/skills/` and rules in `.agents/rules/`.
4. Run `tools/validators/validate_agent_config.py`.

## 9. Relationships and Dependencies

Each role invokes skills in `.agents/skills/`, obeys rules in `.agents/rules/`, and owns specific lifecycle phases in `.agents/config/phase-gates.yaml`.

## 10. Quality Gate

All 19 role files exist, contain all mandatory sections, and reference valid skills and rules.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT grant any Agent permission to bypass `work-items/` or `.agents/rules/source-of-truth.md`.
- Do NOT allow any Agent to mark speculative requirements as `APPROVED`.
