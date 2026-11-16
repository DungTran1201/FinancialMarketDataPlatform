# Agent Role Definitions (`.agents/agents/`)

## 1. Directory Purpose

Defines the 19 specialized AI Agent roles (`AGENT-001..019`) that collaborate across Documentation V2 (`docs/overview/`, `docs/data-plane/`, `docs/application-plane/`, `docs/intelligence-plane/`, `docs/governance/`) and the financial market data platform engineering codebase (`src/`, `frontend/`, `deploy/`, `tests/`).

## 2. Alignment with Documentation V2 RACI Roles

`docs/governance/roles-and-raci.md` defines the 11 canonical accountable RACI roles (`documentation-architect`, `business-analyst`, `system-architect`, `fullstack-engineer`, `data-architect`, `database-architect`, `ai-engineer`, `security-architect`, `qa-lead`, `devops-sre`, `documentation-tooling-engineer`). Each specialized Agent role below maps explicitly to its accountable Documentation V2 RACI role(s).

## 3. Agent Role and Responsibilities

Managed by `documentation-architect` and audited by `documentation-auditor` and `financial-data-platform-reviewer`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating contract and mandatory reading order.
2. `docs/docs-index.yaml` — Plane/domain code roots and governance entrypoints.
3. `docs/governance/roles-and-raci.md` — RACI ownership matrix.
4. `docs/governance/standards/ai-agent-and-discovery-standards.md` — 10-step Agent discovery workflow.
5. `.agents/skill-registry.yaml` and `.agents/config/phase-gates.yaml`.

## 5. Active Agent Roles (19 Roles)

| File | Agent ID | Role Identifier | V2 RACI Alignment |
|---|---|---|---|
| `documentation-architect.md` | `AGENT-001` | `documentation-architect` | `documentation-architect` |
| `discovery-analyst.md` | `AGENT-002` | `discovery-analyst` | `business-analyst` / `system-architect` |
| `requirements-engineer.md` | `AGENT-003` | `requirements-engineer` | `business-analyst` |
| `process-modeler.md` | `AGENT-004` | `process-modeler` | `business-analyst` / `system-architect` |
| `architecture-modeler.md` | `AGENT-005` | `architecture-modeler` | `system-architect` / `ai-engineer` |
| `domain-modeler.md` | `AGENT-006` | `domain-modeler` | `database-architect` / `business-analyst` |
| `api-architect.md` | `AGENT-007` | `api-architect` | `fullstack-engineer` / `system-architect` |
| `ux-modeler.md` | `AGENT-008` | `ux-modeler` | `fullstack-engineer` / `business-analyst` |
| `security-reviewer.md` | `AGENT-009` | `security-reviewer` | `security-architect` |
| `qa-reviewer.md` | `AGENT-010` | `qa-reviewer` | `qa-lead` |
| `documentation-auditor.md` | `AGENT-011` | `documentation-auditor` | `documentation-tooling-engineer` / `documentation-architect` |
| `data-platform-architect.md` | `AGENT-012` | `data-platform-architect` | `data-architect` |
| `data-engineer.md` | `AGENT-013` | `data-engineer` | `data-architect` / `database-architect` |
| `streaming-data-engineer.md` | `AGENT-014` | `streaming-data-engineer` | `data-architect` |
| `lakehouse-engineer.md` | `AGENT-015` | `lakehouse-engineer` | `data-architect` / `database-architect` |
| `analytics-engineer.md` | `AGENT-016` | `analytics-engineer` | `database-architect` / `data-architect` |
| `data-quality-governance-engineer.md` | `AGENT-017` | `data-quality-governance-engineer` | `data-architect` / `qa-lead` |
| `dataops-engineer.md` | `AGENT-018` | `dataops-engineer` | `devops-sre` |
| `financial-data-platform-reviewer.md` | `AGENT-019` | `financial-data-platform-reviewer` | `data-architect` / `qa-lead` |

## 6. Validation Commands

```powershell
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 7. Agent Restrictions

- Do NOT bypass the 10-step discovery workflow in `docs/governance/standards/ai-agent-and-discovery-standards.md` or `docs/governance/source-of-truth-policy.md`.
- Do NOT allow any Agent to mark speculative requirements, unexecuted verifications, or security gaps as `APPROVED`.
