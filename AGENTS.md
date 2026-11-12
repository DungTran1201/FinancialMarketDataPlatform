# AGENTS.md — Root Agent Operating System & Documentation Engineering Contract

## 1. Mission & Engineering Paradigm

This repository (**FinancialMarketDataPlatform**) operates under a strict **README-First, Model-Driven, Template-Governed, Traceability-Enforced, Work-Item-Controlled, Agent-Operated** engineering framework.

Human engineers own business intent, product scope, priority, risk acceptance, and material architectural/security approvals.
AI Agents own evidence discovery, structured decomposition, canonical model updates, template-based document and diagram authoring, cross-artifact synchronization, and deterministic validation.

---

## 2. Mandatory 12-Step Agent Execution Protocol

Before creating or modifying any documentation, canonical model, diagram, or source file, every Agent **MUST** execute the following sequence:

1. **Read Root Instructions**: Read this `AGENTS.md` and `.agents/rules/core.md`.
2. **Read Target Directory `README.md` (README-First Rule)**: Read the `README.md` in the target directory (and parent directory) to understand its scope, authoritative inputs, required templates, and restrictions.
3. **Load Agent Role**: Adopt the designated role definition in `.agents/agents/<role>.md`.
4. **Load Required Skills**: Read the corresponding `SKILL.md` files in `.agents/skills/<skill>/SKILL.md` registered in `.agents/skill-registry.yaml`.
5. **Inspect Authoritative Sources**: Read upstream canonical models (`models/`), shared platform specifications (`docs/architecture/`, `docs/specifications/`), and product lifecycle documents (`docs/product/`).
6. **Initialize or Update a Work Item**: For any non-trivial change, create or update `work-items/<TYPE>-<NNN>-<slug>/` following `work-items/README.md`.
7. **Select Required Artifacts from the Artifact Matrix**: Populate `artifact-plan.yaml` using `.agents/config/artifact-matrix.yaml` and `.agents/config/change-types.yaml` — never blindly generate every possible document.
8. **Update Canonical Models First**: Update or create structured YAML models in `models/` before updating derived prose or diagrams.
9. **Author or Synchronize Documents & Diagrams from Templates**: Use the exact template from `docs/templates/` and register diagrams in `docs/diagrams/`.
10. **Run Automated Validators**: Execute `.\.venv\Scripts\python.exe tools/validators/run_all.py` and resolve all errors.
11. **Update Status & Bidirectional Traceability**: Synchronize IDs (`identifier-registry.yaml`) and status transitions (`status-lifecycle.yaml`).
12. **Report Unresolved Issues Explicitly**: Record any `ASSUMPTION` or `OPEN QUESTION` in the discovery/governance registers; never invent business facts.

---

## 3. Source-of-Truth Hierarchy & Conflict Resolution

When artifacts disagree, authority is resolved in the following strict order (see `.agents/rules/source-of-truth.md`):

1. **Approved Requirements, Business Rules & Acceptance Criteria** (`docs/specifications/`, `docs/product/02-requirements/`, `models/requirements/`).
2. **Approved Architecture Decision Records (ADRs)** (`docs/architecture/adr/ADR-001..006`, `docs/product/06-architecture/`).
3. **Canonical Structured Models** (`models/**/*.yaml`) — authoritative machine-readable representation of entities, APIs, states, and components.
4. **Verified Production/Repository Code & Infrastructure Configs** (`src/`, `deploy/`, `docker-compose.yml`) — authoritative evidence of *current implemented behavior* (`AS-IS`).
5. **Authoritative Human-Readable Specifications** (`docs/architecture/`, `docs/product/`, `docs/features/`).
6. **Derived Visual Diagrams** (`docs/diagrams/`) — **never** a standalone source of truth; must always reflect upstream models and documents.
7. **AI Inference** — permitted **only** when explicitly tagged as `[ASSUMPTION — REQUIRES VALIDATION]` or `[PROPOSED — NOT APPROVED]`.

---

## 4. Fact Classification Discipline

Every statement captured during discovery, requirements, or design must be classified as one of:
- `FACT`: Verified directly from repository files, approved specifications, or explicit user confirmation.
- `ASSUMPTION`: A reasonable working hypothesis tagged `[ASSUMPTION — REQUIRES VALIDATION]`.
- `DECISION`: A recorded engineering or product choice linked to an `ADR-###` or decision log entry.
- `OPEN QUESTION`: An unresolved ambiguity tagged `[OPEN QUESTION]` that requires human sign-off.

**Prohibition**: Never silently convert an `ASSUMPTION` or `OPEN QUESTION` into an approved `FACT`.

---

## 5. Repository Subsystem Map

| Subsystem Root | Architectural Role | Governing Config / Index |
|---|---|---|
| `.agents/` | Agent Operating System (Roles, Rules, Skills, Configs, Hooks) | [.agents/README.md](.agents/README.md) |
| `docs/` | Master Human-Readable Documentation Space | [docs/README.md](docs/README.md) |
| `docs/architecture/` | Shared Data Platform, Backend & Agent Architecture (Preserved Baseline) | [docs/architecture/README.md](docs/architecture/README.md) |
| `docs/specifications/` | Shared Data Platform & API Specifications (Preserved Baseline) | [docs/specifications/README.md](docs/specifications/README.md) |
| `docs/product/` | 15-Phase Product & Website Engineering Lifecycle (`00` $\rightarrow$ `14`) | [docs/product/README.md](docs/product/README.md) |
| `docs/features/` | Self-Contained Feature Documentation Packages | [docs/features/README.md](docs/features/README.md) |
| `docs/templates/` | Centralized Reusable Document Template Library (14 Categories) | [docs/templates/README.md](docs/templates/README.md) |
| `docs/diagrams/` | Unified Technical Diagram Subsystem (`DIAG-*`) | [docs/diagrams/README.md](docs/diagrams/README.md) |
| `models/` | Canonical Machine-Readable YAML Models (12 Categories) | [models/README.md](models/README.md) |
| `work-items/` | Change Intake, Discovery, Impact, Artifact Plan & Gate Tracking | [work-items/README.md](work-items/README.md) |
| `tools/` | Automated Documentation Validators & Lifecycle Hooks | [tools/README.md](tools/README.md) |

---

## 6. Validation & Quality Gate Commands

```powershell
# Run the complete Documentation Engineering validation suite
.\.venv\Scripts\python.exe tools/validators/run_all.py

# Run architectural boundary and contract unit tests
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

