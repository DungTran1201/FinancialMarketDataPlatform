# Agent Workspace Operating System (`.agents/`)

This directory hosts the restored and Documentation V2-aligned **Agent Operating System** alongside workspace execution hooks. Normative documentation rules, schemas, applicability criteria, and RACI ownership reside in `docs/governance/` and [../AGENTS.md](../AGENTS.md).

## 1. Authoritative Documentation V2 Entrypoints

- **Agent Operating Contract**: [../AGENTS.md](../AGENTS.md)
- **Documentation Root**: [../docs/README.md](../docs/README.md)
- **Machine-Readable Docs Index**: [../docs/docs-index.yaml](../docs/docs-index.yaml)
- **Governance Architecture & Policies**: [../docs/governance/README.md](../docs/governance/README.md)
- **AI Agent & Discovery Standards**: [../docs/governance/standards/ai-agent-and-discovery-standards.md](../docs/governance/standards/ai-agent-and-discovery-standards.md)
- **Risk-Based Applicability Matrix**: [../docs/governance/catalog/artifact-applicability-matrix.yaml](../docs/governance/catalog/artifact-applicability-matrix.yaml)

## 2. Directory Responsibilities

| Path | Responsibility | Index / Manifest |
|---|---|---|
| `.agents/agents/` | 19 specialized Agent role definitions (`AGENT-001..019`) mapped to Documentation V2 RACI roles and Plane/Domain/Capability directories | [agents/README.md](agents/README.md) |
| `.agents/rules/` | 22 operational guardrails (`RULE-001..010` and `DATA-RULE-001..012`) aligned with `docs/governance/` | [rules/README.md](rules/README.md) |
| `.agents/skills/` | 25 modular skill packages (`SKILL.md` + `README.md`) providing repeatable engineering and documentation procedures | [skills/README.md](skills/README.md) |
| `.agents/config/` | 7 operational YAML registries mapping V2 Planes/Domains/Capabilities, boundaries, IDs, gates, and decoupled status enums | [config/README.md](config/README.md) |
| `.agents/catalog/` | External skill evaluation, path sanitization, and quarantine provenance policy | [catalog/README.md](catalog/README.md) |
| `hooks.json` | Registers `pre_command_guard.py`, `post_doc_write_check.py`, and `stop_readiness_check.py` | [hooks.json](hooks.json) |
| `skill-registry.yaml` | Authoritative active/inactive skill registration list (`25` active skills) | [skill-registry.yaml](skill-registry.yaml) |
| `skills_manifest.json` | Machine-readable mapping of skill IDs, `SKILL.md` paths, V2 lifecycle stages, and owner roles | [skills_manifest.json](skills_manifest.json) |

## 3. Agent Role Selection

Select the active role in [agents/README.md](agents/README.md) matching the task scope, and verify final accountability against [../docs/governance/roles-and-raci.md](../docs/governance/roles-and-raci.md):

- **Governance, Discovery & Requirements**: `documentation-architect`, `discovery-analyst`, `requirements-engineer`, `process-modeler`, `documentation-auditor`
- **Architecture, Domain, APIs & UX**: `architecture-modeler`, `domain-modeler`, `api-architect`, `ux-modeler`
- **Security & Verification**: `security-reviewer`, `qa-reviewer`, `financial-data-platform-reviewer`
- **Data Platform Specialists**: `data-platform-architect`, `data-engineer`, `streaming-data-engineer`, `lakehouse-engineer`, `analytics-engineer`, `data-quality-governance-engineer`, `dataops-engineer`

## 4. Rule Loading and Priority

1. **Highest Authority**: [../AGENTS.md](../AGENTS.md) and [../docs/governance/](../docs/governance/README.md) take precedence over all `.agents/` files. If any `.agents/` note conflicts with `docs/governance/`, `docs/governance/` wins and the discrepancy MUST be logged.
2. **Always-Active Operational Rules**: Core discovery, source-of-truth, security, and status separation rules (`RULE-001..010`).
3. **Domain-Scoped Data Rules**: Load each role's **Primary (Always Load)** rules and **Task-Scoped** rules (`DATA-RULE-001..012`) only for touched subsystems.

## 5. Skill Discovery and Execution

1. Confirm the skill is active in [skill-registry.yaml](skill-registry.yaml) and indexed in [skills_manifest.json](skills_manifest.json).
2. Read `.agents/skills/<skill>/SKILL.md` directly (read `.agents/skills/<skill>/README.md` only when editing the skill package).
3. Follow the 10-step Agent discovery workflow in [../docs/governance/standards/ai-agent-and-discovery-standards.md](../docs/governance/standards/ai-agent-and-discovery-standards.md) before modifying any file.
4. External or third-party skills MUST pass quarantine review in [catalog/external-skill-policy.md](catalog/external-skill-policy.md) before admission.

## 6. Configuration Registries (`.agents/config/`)

- [config/document-map.yaml](config/document-map.yaml): Maps `docs/overview/`, `docs/data-plane/`, `docs/application-plane/`, `docs/intelligence-plane/`, `docs/governance/templates/`, and all 10 capability directories.
- [config/artifact-matrix.yaml](config/artifact-matrix.yaml): Operational routing aligned with [../docs/governance/catalog/artifact-applicability-matrix.yaml](../docs/governance/catalog/artifact-applicability-matrix.yaml).
- [config/change-types.yaml](config/change-types.yaml): Maps V2 work types and assessment signals to `LOW | MEDIUM | HIGH_CRITICAL` risk tiers.
- [config/data-platform-boundaries.yaml](config/data-platform-boundaries.yaml): Enforces Three-Plane code/storage ownership, `EventEnvelopeV1`, and Medallion responsibilities.
- [config/identifier-registry.yaml](config/identifier-registry.yaml): Aligns `doc_id`, `CAP-*`, `FR/BR/NFR/RULE/UC/AC/THR/SEC/TS/TC`, `ADR-*`, and `DIAG-*` patterns.
- [config/phase-gates.yaml](config/phase-gates.yaml) & [config/status-lifecycle.yaml](config/status-lifecycle.yaml): Mirror the 9-stage V2 lifecycle, `QG-1-SCOPE..QG-7-OPS`, and decoupled `status` / `implementation_status` enums.

## 7. Documentation V2 Integration & Source-of-Truth Precedence

Per [../docs/governance/source-of-truth-policy.md](../docs/governance/source-of-truth-policy.md):

- **`docs/governance/`** is authoritative for documentation rules, schemas, templates, and RACI.
- **`APPROVED` capability specs, contracts (`openapi.yaml`, `asyncapi.yaml`, `data-contract.yaml`), and ADRs** govern **`TARGET`** intent.
- **Verified code (`src/`, `frontend/`), DDL/IaC (`deploy/`, `docker-compose.yml`), and executed tests (`tests/`)** govern **`AS-IS`** current reality.
- **Diagrams** are always derived (`is_authoritative: false`).

## 8. Hooks & Validation Workflow

- [hooks.json](hooks.json): Registers `pre_command_guard.py`, `post_doc_write_check.py`, and `stop_readiness_check.py` (delegating documentation verification to `scripts/docs/validate_docs.py` via `tools/validators/run_all.py`).

Run these checks after modifying documentation, schemas, templates, Agent OS configs, or tests:

```powershell
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
.\.venv\Scripts\python.exe -m pytest tests/ -v
```
