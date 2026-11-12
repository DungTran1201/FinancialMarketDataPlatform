# Skill Package: Automated Documentation & Model Validation (`.agents/skills/documentation-validation/`)

## 1. Directory Purpose

Provides the reusable execution procedure for **Automated Documentation & Model Validation** (`SKILL-016`). Runs the deterministic validator suite (`tools/validators/run_all.py`) and triages structural or semantic errors.

## 2. Scope and Boundaries

- **Belongs in this directory**: `SKILL.md` and `README.md` for `documentation-validation`.
- **Does NOT belong in this directory**: Actual project specifications, canonical models, or work-item records.

## 3. Agent Role and Responsibilities

Primary owning Agent role: `documentation-auditor` (`.agents/agents/documentation-auditor.md`).

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating protocol.
2. `.agents/agents/documentation-auditor.md` — Owning role definition.
3. `tools/validators/` — Associated template or tool location.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `SKILL.md` | Executable instruction specification for `documentation-validation` | Required | `.agents/skills/documentation-validation/SKILL.md` |

## 6. Directory and File Organization

Contains `README.md` and `SKILL.md` inside `.agents/skills/documentation-validation/`.

## 7. Document Creation Rules

`SKILL.md` must begin with YAML frontmatter (`name`, `description`) and contain all 10 standard skill sections.

## 8. Creation Workflow

1. Read `.agents/skills/documentation-validation/README.md` and `SKILL.md`.
2. Verify preconditions and authoritative inputs.
3. Execute the numbered procedure in `SKILL.md`.
4. Run `tools/validators/run_all.py` to verify output compliance.

## 9. Relationships and Dependencies

Registered in `.agents/skill-registry.yaml` and invoked during lifecycle phase `14-governance`.

## 10. Quality Gate

`SKILL.md` contains valid frontmatter and all required sections, passing `validate_agent_config.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT bypass target directory `README.md` instructions when executing this skill.
- Do NOT fabricate requirements or mark unverified outputs as `APPROVED`.
