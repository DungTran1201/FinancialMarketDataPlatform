# Agent Operating System (`.agents/`)

## 1. Directory Purpose

`.agents/` is the Agent Governance and Operating System for `FinancialMarketDataPlatform`. It defines the specialized AI Agent roles (`agents/`), mandatory behavioral constraints (`rules/`), reusable engineering procedures (`skills/`), machine-readable workflow registries (`config/`), external skill policies (`catalog/`), and execution lifecycle hooks (`hooks.json`).

## 2. Scope and Boundaries

- **Belongs in this directory**: Agent role definitions, operating rules, skill packages, workflow YAML registries, skill catalogs, and lifecycle hooks.
- **Does NOT belong in this directory**: Product requirements, system architecture documents (`docs/`), canonical domain models (`models/`), or application code (`src/`).

## 3. Agent Role and Responsibilities

Owned by `documentation-architect` and audited by `documentation-auditor`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root repository Agent operating contract.
2. `work-items/DOCS-001-documentation-engineering-foundation/discovery.md` — Reference architecture audit.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `agents/` | 11 specialized Agent role definitions | Required | `.agents/agents/README.md` |
| `rules/` | 10 mandatory operating rules | Required | `.agents/rules/README.md` |
| `skills/` | 16 discipline-specific SKILL.md packages | Required | `.agents/skills/README.md` |
| `config/` | 6 YAML configuration registries | Required | `.agents/config/README.md` |
| `catalog/` | External skill governance and sourcing policy | Required | `.agents/catalog/README.md` |
| `hooks.json` | Pre/Post tool execution and stop-readiness hooks | Required | `.agents/hooks.json` |
| `skill-registry.yaml` | Registry of active and candidate skills | Required | `.agents/skill-registry.yaml` |
| `skills_manifest.json` | Machine-readable skill metadata manifest | Required | `.agents/skills_manifest.json` |

## 6. Directory and File Organization

Organized into five subdirectories (`agents/`, `rules/`, `skills/`, `config/`, `catalog/`) plus three root manifest files (`hooks.json`, `skill-registry.yaml`, `skills_manifest.json`).

## 7. Document Creation Rules

Every skill in `skills/` must be registered in both `skill-registry.yaml` and `skills_manifest.json`. Every role in `agents/` must reference valid skills and rules.

## 8. Creation Workflow

1. Read `AGENTS.md` and `.agents/README.md`.
2. Verify target Agent role, rule, or skill against `.agents/config/` registries.
3. Create or update the artifact following its subsystem README contract.
4. Synchronize `skill-registry.yaml` and `skills_manifest.json` when modifying skills.
5. Run `tools/validators/validate_agent_config.py`.

## 9. Relationships and Dependencies

Governs how Agents interact with `work-items/`, `models/`, `docs/`, `docs/diagrams/`, and `tools/`.

## 10. Quality Gate

All roles, rules, skills, configs, and hooks pass `validate_agent_config.py` and `validate_readmes.py` with zero errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT add product-specific companion/avatar/Discord skills unrelated to FinancialMarketDataPlatform.
- Do NOT register a skill in `skill-registry.yaml` unless its `SKILL.md` exists on disk.
- Do NOT create rules that contradict `AGENTS.md` or `.agents/rules/source-of-truth.md`.
