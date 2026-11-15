# Development & Engineering Portal (`docs/development/`)

## 1. Directory Purpose

`docs/development/` is the developer onboarding, local environment, and engineering contribution guide for the **FinancialMarketDataPlatform**. It guides engineers from a fresh repository clone to running tests, contributing new features, and validating documentation against the Clean Architecture rules.

## 2. Scope and Boundaries

- **Belongs in `docs/development/`**:
  - Local environment quickstart (Python venv, Node/npm, Docker).
  - Comprehensive codebase directory and responsibility map.
  - Test execution guidelines (unit, contract, integration, DQ, performance).
  - Contribution and branch workflow instructions.
- **Does NOT belong in `docs/development/`**:
  - Architecture theory or deep ADR design decisions (which live in `docs/architecture/`).
  - Production container deployment runbooks (which live in `docs/operations/`).
  - Raw canonical YAML models (which live in `models/`).

## 3. Agent Role and Responsibilities

- **Primary Owning Role**: `documentation-architect`.
- **Collaborating Roles**: `data-engineer`, `system-architect`.
- **Responsibilities**:
  - Ensure developer setup commands are completely accurate, tested, and reproducible on both Windows and Linux.
  - Document repository organization and architectural layer boundaries.

## 4. Authoritative Inputs

1. [pyproject.toml](../../pyproject.toml) — Python project dependencies and tool configs.
2. [frontend/package.json](../../frontend/package.json) — Frontend dependencies and build scripts.
3. [AGENTS.md](../../AGENTS.md) — Agent Operating System and execution protocol.
4. [tests/README.md](../../tests/README.md) — Automated verification subsystem contract.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Domain scope, inputs, and navigation index | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `developer-quickstart.md` | 5-minute setup, local venv, npm commands, test cheat-sheet | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `codebase-map.md` | Structural directory map and responsibility breakdown | Required | `docs/templates/architecture/C4-component.template.md` |

## 6. Directory and File Organization

```text
docs/development/
├── README.md               # Domain overview & 12-section contract
├── developer-quickstart.md # Local environment setup & quickstart
└── codebase-map.md         # Architecture directory & component map
```

## 7. Document Creation Rules

- All setup commands must be reproducible and tested on both Windows PowerShell and Linux Bash.
- Never document deprecated commands or uninstalled scripts.

## 8. Creation Workflow

1. Test setup commands locally from scratch.
2. Author documentation with clear step-by-step instructions.
3. Validate links and run `tools/validators/run_all.py`.

## 9. Relationships and Dependencies

- **Upstream**: Governed by `pyproject.toml`, `frontend/package.json`, and `AGENTS.md`.
- **Downstream**: The primary starting point for all new human engineers and agents.

## 10. Quality Gate

- All listed commands verified against local virtual environment and package descriptors.
- Zero broken links.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/validate_readmes.py
.\.venv\Scripts\python.exe tools/validators/run_all.py
```

## 12. Agent Restrictions

- **Do NOT** omit prerequisites or platform-specific installation details.
- **Do NOT** recommend bypass flags (such as `--no-verify`).
