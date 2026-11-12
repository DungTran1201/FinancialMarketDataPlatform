# External Skill Catalog & Quarantine Policy (`.agents/catalog/`)

## 1. Directory Purpose

Governs how external or third-party Agent skills are evaluated, quarantined, sanitized, and approved before admission into `.agents/skills/`.

## 2. Scope and Boundaries

- **Belongs in this directory**: `skill-sources.md` and `external-skill-policy.md`.
- **Does NOT belong in this directory**: Active workspace skills (which belong in `.agents/skills/`).

## 3. Agent Role and Responsibilities

Managed by `documentation-architect` and reviewed by `security-reviewer`.

## 4. Authoritative Inputs

1. `AGENTS.md` — Root safety and governance contract.
2. `.agents/rules/security.md` — Security and isolation rules.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `skill-sources.md` | Provenance log of adapted and evaluated skill patterns | Required | `.agents/catalog/README.md` |
| `external-skill-policy.md` | Security and quarantine policy for external skills | Required | `.agents/catalog/README.md` |

## 6. Directory and File Organization

Contains `README.md`, `skill-sources.md`, and `external-skill-policy.md`.

## 7. Document Creation Rules

Every external skill candidate must have its provenance, license/source, and domain contamination audit recorded in `skill-sources.md`.

## 8. Creation Workflow

1. Read `.agents/catalog/README.md` and `external-skill-policy.md`.
2. Audit external skill candidates for hardcoded paths, secrets, or unrelated product logic.
3. Record provenance in `skill-sources.md` before adapting into `.agents/skills/`.
4. Run `tools/validators/validate_agent_config.py`.

## 9. Relationships and Dependencies

Protects `.agents/skills/` and `.agents/skill-registry.yaml` from unvetted or contaminated external instructions.

## 10. Quality Gate

Both policy documents exist and pass `validate_readmes.py` and `validate_docs.py`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_agent_config.py
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- Do NOT activate an external skill directly without adapting its paths and rules to `FinancialMarketDataPlatform`.
- Do NOT import product-specific rules or skills from external repositories.
