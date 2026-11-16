# AGENTS.md — AI Agent Documentation & Repository Contract

`FinancialMarketDataPlatform` uses **Documentation V2** as its single authoritative documentation engineering system. Detailed rules, schemas, templates, and applicability criteria reside under [docs/governance/](docs/governance/README.md) rather than being duplicated in this file.

---

## 1. Mandatory Reading Order

Before creating or updating documentation, specifications, or contracts, AI Agents MUST read in sequence:

1. [AGENTS.md](AGENTS.md) — Root repository agent contract.
2. [docs/README.md](docs/README.md) — Documentation V2 entrypoint and current lifecycle phase status.
3. [docs/docs-index.yaml](docs/docs-index.yaml) — Machine-readable plane/code mapping and active governance paths.
4. [docs/governance/documentation-architecture.md](docs/governance/documentation-architecture.md) — `Platform -> Plane -> Domain -> Capability` scoping rules.
5. [docs/governance/source-of-truth-policy.md](docs/governance/source-of-truth-policy.md) — Authority precedence when docs, contracts, and code conflict.
6. [docs/governance/standards/README.md](docs/governance/standards/README.md) and [docs/governance/standards/ai-agent-and-discovery-standards.md](docs/governance/standards/ai-agent-and-discovery-standards.md) — Domain/task-scoped standards, discovery rules, and prompt/citation discipline.
7. [docs/governance/catalog/artifact-applicability-matrix.yaml](docs/governance/catalog/artifact-applicability-matrix.yaml) — Risk tier and signal-driven artifact requirements before creating any specification or template instance.

---

## 2. Current Documentation Phase Status

- **Active Phase**: `PHASE_2_ACTIVE` (Governance foundation complete; `docs/overview/`, `docs/data-plane/`, `docs/application-plane/`, and `docs/intelligence-plane/` are active in `DRAFT` / `IN_REVIEW` status pending formal acceptance).
- **Prohibition**: Agents MUST NOT create empty placeholder folders, speculative ungrounded claims, or `docs/archive/` directories.

---

## 3. Non-Negotiable Operating Rules for Agents

1. **Inspect Code, Configs & Tests First**: Agents MUST inspect actual files in `src/`, `frontend/`, `deploy/`, `tests/`, and `pyproject.toml` before stating any `AS-IS` implemented behavior. Never infer implementation from legacy docs or file names alone.
2. **Respect Source-of-Truth & Reality**:
   - Approved specifications, contracts, and ADRs govern **TARGET** intent.
   - Verified code, runtime configuration, and test runs govern **AS-IS** current reality.
   - Document Status (`DRAFT | IN_REVIEW | APPROVED | DEPRECATED`) MUST remain separate from Implementation Status (`PLANNED | NOT_IMPLEMENTED | SIMULATED | PARTIALLY_IMPLEMENTED | IMPLEMENTED | VERIFIED`).
3. **Zero Silent Assumptions or Security Whitewashing**:
   - Unconfirmed hypotheses MUST be tagged `[ASSUMPTION]` with owner and validation plan.
   - Missing decisions, thresholds, or policies MUST remain explicitly logged as `OPEN`, `NEEDS_CLARIFICATION`, or `BLOCKED`.
   - Insecure current behavior MUST be reported as a gap, never described as an approved security control.
   - Real secrets, private keys, tokens, or PII MUST NEVER be placed in docs or tests.
4. **Prevent Duplication & Monoliths**: Author specifications at the narrowest owning scope defined in [documentation-architecture.md](docs/governance/documentation-architecture.md) and choose only applicable artifacts per [artifact-applicability-matrix.yaml](docs/governance/catalog/artifact-applicability-matrix.yaml).
5. **Follow Agent OS & Lifecycle Hooks**: Workspace lifecycle hooks are defined in [.agents/hooks.json](.agents/hooks.json), and Documentation V2-aligned Agent roles, rules, skills, and configuration registries are indexed in [.agents/README.md](.agents/README.md). Legacy V1 `models/` and `work-items/` trees remain retired in Git history (`f0329d3b`, `dde3e816`).

---

## 4. Required Validation & Test Commands

Run these checks after modifying documentation, schemas, templates, validators, or tests:

```powershell
# Documentation V2 schema, link, applicability & structural validator
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py

# Documentation CI compatibility wrapper
.\.venv\Scripts\python.exe tools/validators/run_all.py

# Full repository verification suite (includes tests/docs/)
.\.venv\Scripts\python.exe -m pytest tests/ -v
```
