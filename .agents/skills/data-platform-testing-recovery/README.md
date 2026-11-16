# Skill Package: Data Platform Testing & Recovery Verification (`.agents/skills/data-platform-testing-recovery/`)

## 1. Directory Purpose

Provides the reusable execution procedure for **Data Platform Testing & Recovery Verification** (`SKILL-020`). Tests data pipeline correctness and operational recovery, including replay, duplicates, late events, sink failure windows, backfills, and cross-plane isolation.

## 2. Scope and Boundaries

- **Belongs in this directory**: `SKILL.md` and `README.md` for `data-platform-testing-recovery`.
- **Does NOT belong in this directory**: Application runtime code, product specifications, or global governance policies (`docs/governance/`).

## 3. Agent Role and Responsibilities

Primary owning Agent role: `financial-data-platform-reviewer` (`.agents/agents/financial-data-platform-reviewer.md`).

## 4. Authoritative Inputs

1. `AGENTS.md` — Root Agent operating contract and mandatory reading order.
2. `.agents/agents/financial-data-platform-reviewer.md` — Owning role definition.
3. `docs/data-plane/operations/test-plan.md` and `tests/` — Associated Documentation V2 templates, schemas, contracts, or code locations.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `SKILL.md` | Executable instruction specification for `data-platform-testing-recovery` | Required | `.agents/skills/data-platform-testing-recovery/SKILL.md` |

## 6. Directory and File Organization

Contains `README.md` and `SKILL.md` inside `.agents/skills/data-platform-testing-recovery/`.

## 7. Document Creation Rules

`SKILL.md` must begin with YAML frontmatter (`name`, `description`) and contain all 10 standard skill sections aligned to Documentation V2.

## 8. Creation Workflow

1. Read `.agents/skills/data-platform-testing-recovery/SKILL.md` (and this `README.md` when modifying the skill package).
2. Verify preconditions, owning `capability.yaml`, and authoritative inputs.
3. Execute the numbered procedure in `SKILL.md`.
4. Run `scripts/docs/validate_docs.py` (or `tools/validators/run_all.py`) to verify Documentation V2 compliance.

## 9. Relationships and Dependencies

Registered in `.agents/skill-registry.yaml` and `.agents/skills_manifest.json`, and invoked during Documentation V2 lifecycle stage `7-verification`.

## 10. Quality Gate

`SKILL.md` contains valid frontmatter, all 10 required sections, zero stale V1 path contradictions, and aligns with `AGENTS.md` and `docs/governance/`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT bypass the 10-step discovery workflow in `docs/governance/standards/ai-agent-and-discovery-standards.md`.
- Do NOT fabricate requirements, metrics, or mark unverified outputs as `APPROVED` or `VERIFIED`.
