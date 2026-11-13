# Skill Package: DataOps, Observability & Recovery Operations (`.agents/skills/dataops-observability/`)

## 1. Directory Purpose

Provides the reusable execution procedure for **DataOps, Observability & Recovery Operations** (`SKILL-021`). Operates streaming and batch data services with actionable metrics, bounded-cardinality telemetry, freshness/lag alerts, runbooks, and recovery tests.

## 2. Scope and Boundaries

- **Belongs in this directory**: `SKILL.md` and `README.md` for `dataops-observability`.
- **Does NOT belong in this directory**: Application runtime code, product requirements, or global rules.

## 3. Agent Role and Responsibilities

Primary owning Agent role: `dataops-engineer` (`.agents/agents/dataops-engineer.md`).

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating protocol.
2. `.agents/agents/dataops-engineer.md` — Owning role definition.
3. `docs/templates/operations/` and `deploy/` — Associated template and deployment locations.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `SKILL.md` | Executable instruction specification for `dataops-observability` | Required | `.agents/skills/dataops-observability/SKILL.md` |

## 6. Directory and File Organization

Contains `README.md` and `SKILL.md` inside `.agents/skills/dataops-observability/`.

## 7. Document Creation Rules

`SKILL.md` must begin with YAML frontmatter (`name`, `description`) and contain all 10 standard skill sections.

## 8. Creation Workflow

1. Read `.agents/skills/dataops-observability/README.md` and `SKILL.md`.
2. Verify preconditions and authoritative inputs.
3. Execute the numbered procedure in `SKILL.md`.
4. Run `tools/validators/run_all.py` to verify output compliance.

## 9. Relationships and Dependencies

Registered in `.agents/skill-registry.yaml` and `.agents/skills_manifest.json`, and invoked during lifecycle phase `13-operations`.

## 10. Quality Gate

`SKILL.md` contains valid frontmatter and all required sections, passing `validate_agent_config.py`.

## 11. Validation Commands

```powershell
python tools/validators/validate_agent_config.py
python tools/validators/validate_readmes.py
python tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT bypass target directory `README.md` instructions when executing this skill.
- Do NOT fabricate requirements or mark unverified outputs as `APPROVED`.

