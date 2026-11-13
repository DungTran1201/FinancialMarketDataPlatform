# Skill Package: Lakehouse Medallion Engineering (`.agents/skills/lakehouse-medallion/`)

## 1. Directory Purpose

Provides the reusable execution procedure for **Lakehouse Medallion Engineering** (`SKILL-025`). Engineers MinIO/S3, Parquet, and Apache Iceberg lakehouse layers with immutable Bronze, standardized Silver, PySpark backfills, and safe table maintenance.

## 2. Scope and Boundaries

- **Belongs in this directory**: `SKILL.md` and `README.md` for `lakehouse-medallion`.
- **Does NOT belong in this directory**: Application runtime code, product requirements, or global rules.

## 3. Agent Role and Responsibilities

Primary owning Agent role: `lakehouse-engineer` (`.agents/agents/lakehouse-engineer.md`).

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating protocol.
2. `.agents/agents/lakehouse-engineer.md` — Owning role definition.
3. `src/consumers/lakehouse_bronze/` and `src/processing/spark/` — Associated Bronze consumer and PySpark job locations.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `SKILL.md` | Executable instruction specification for `lakehouse-medallion` | Required | `.agents/skills/lakehouse-medallion/SKILL.md` |

## 6. Directory and File Organization

Contains `README.md` and `SKILL.md` inside `.agents/skills/lakehouse-medallion/`.

## 7. Document Creation Rules

`SKILL.md` must begin with YAML frontmatter (`name`, `description`) and contain all 10 standard skill sections.

## 8. Creation Workflow

1. Read `.agents/skills/lakehouse-medallion/README.md` and `SKILL.md`.
2. Verify preconditions and authoritative inputs.
3. Execute the numbered procedure in `SKILL.md`.
4. Run `tools/validators/run_all.py` to verify output compliance.

## 9. Relationships and Dependencies

Registered in `.agents/skill-registry.yaml` and `.agents/skills_manifest.json`, and invoked during lifecycle phase `07-domain`.

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

