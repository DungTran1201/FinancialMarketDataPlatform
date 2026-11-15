# Work Item DOCS-003: Documentation Consistency & Architecture Remediation

## 1. Directory Purpose

`work-items/DOCS-003-documentation-consistency-remediation/` contains the authoritative governance, audit registers, impact assessments, remediation matrices, and verification reports for Work Item **DOCS-003**. This work item audits and resolves all 14 technical inconsistencies across the platform's documentation, canonical models, technical diagrams, container deployment files, and source code.

## 2. Scope and Boundaries

- **Belongs in this directory**:
  - Mandatory work-item lifecycle files (`request.md`, `discovery.md`, `impact-analysis.md`, `artifact-plan.yaml`, `implementation-plan.md`, `verification-plan.md`, `review.md`, `state.yaml`, `README.md`).
  - Specialized consistency registers (`baseline-snapshot.md`, `canonical-source-register.yaml`, `remediation-matrix.csv`, `remediation-matrix.md`, `identifier-audit.md`, `technical-consistency-audit.md`, `diagram-consistency-audit.md`, `documentation-overlap-audit.md`, `link-integrity-audit.md`, `remediation-validation-report.md`).
- **Does NOT belong in this directory**:
  - Global documentation pages (which live under `docs/`).
  - Canonical models (which live under `models/`).
  - Runtime application or test code (which lives under `src/` or `tests/`).

## 3. Agent Role and Responsibilities

- **Primary Owning Roles**: `Lead Documentation Architect`, `System Architect`, `Data Platform Architect`.
- **Collaborating Roles**: `Diagram Engineer`, `Traceability Auditor`, `QA & Validation Engineer`.
- **Responsibilities**:
  - Audit and remediate all 14 historical discrepancies.
  - Enforce the single source of truth hierarchy across all technical domains.
  - Maintain 100% backward compatibility and zero identifier breaking changes.
  - Ensure zero regressions across all 10 automated documentation validators.

## 4. Authoritative Inputs

1. `AGENTS.md` and `.agents/rules/` — Root governance framework.
2. `models/architecture/components.yaml` and `models/data-platform/topics.yaml`.
3. `src/lakehouse/orchestration/pipeline.py` and `src/streaming/contracts/topics.py`.
4. `docker-compose.yml` — Authoritative container and service definitions.
5. `tools/validators/` — 10-validator automated quality gate suite.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Work item directory index and 12-section operating contract | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `request.md` | Intake request, background, scope, and non-negotiable constraints | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `discovery.md` | 14-finding audit register, fact classifications, and decision log | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `impact-analysis.md` | Cross-subsystem impact analysis, risk assessment, and mitigation | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `artifact-plan.yaml` | Machine-readable manifest of created and updated artifacts | Required | `work-items/_template/artifact-plan.yaml` |
| `implementation-plan.md` | Phased remediation strategy across 6 execution phases | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `verification-plan.md` | Verification checklist and quality gate criteria | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `review.md` | Phase gate audit sign-off (G0 through G6) | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `remediation-review.md` | Detailed remediation review companion document | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `state.yaml` | Work item lifecycle state machine tracking status through DONE | Required | `work-items/_template/state.yaml` |
| `baseline-snapshot.md` | Pre-remediation repository inventory and validator baseline | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `canonical-source-register.yaml` | Authoritative single-source-of-truth mapping across all domains | Required | `work-items/_template/artifact-plan.yaml` |
| `remediation-matrix.csv` | Machine-readable artifact-by-artifact remediation register | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `remediation-matrix.md` | Human-readable remediation matrix and rationale | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `identifier-audit.md` | Full-inventory audit across all 21 ID namespaces | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `technical-consistency-audit.md` | Technical consistency audit across code, models, and docs | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `diagram-consistency-audit.md` | Diagram alignment audit against streaming and pipeline logic | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `documentation-overlap-audit.md` | Non-duplication and domain boundary audit across 9 doc portals | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `link-integrity-audit.md` | Full repository link graph and relative path validation | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `remediation-validation-report.md` | Automated test suite and validator execution evidence | Required | `docs/templates/architecture/architecture-overview.template.md` |

## 6. Directory and File Organization

```text
work-items/DOCS-003-documentation-consistency-remediation/
├── README.md                          # Directory index & 12-section contract
├── request.md                         # Intake request and constraints
├── discovery.md                       # 14-finding audit & fact register
├── impact-analysis.md                 # Cross-subsystem impact analysis
├── artifact-plan.yaml                 # Machine-readable artifact manifest
├── implementation-plan.md             # Phased execution plan
├── verification-plan.md               # Quality gate checklist
├── review.md                          # Phase gate sign-off
├── remediation-review.md              # In-depth remediation review
├── state.yaml                         # Lifecycle state machine
├── baseline-snapshot.md               # Commit f0329d3 inventory snapshot
├── canonical-source-register.yaml     # Single-source-of-truth register
├── remediation-matrix.csv             # Machine-readable remediation register
├── remediation-matrix.md              # Human-readable remediation register
├── identifier-audit.md                # 21-namespace ID preservation audit
├── technical-consistency-audit.md     # Code vs models vs docs audit
├── diagram-consistency-audit.md       # Diagram vs model & pipeline audit
├── documentation-overlap-audit.md     # Boundary & non-duplication audit
├── link-integrity-audit.md            # Link graph & relative link audit
└── remediation-validation-report.md   # Quality gate & validator report
```

## 7. Document Creation Rules

- Every artifact must be authored with explicit metadata tables and headers.
- No placeholder tokens (`TODO`, `TBD`, `FIXME`) are permitted.
- All IDs must strictly adhere to the preserved 21 namespaces in `identifier-registry.yaml`.

## 8. Creation Workflow

1. Perform discovery and log facts in `discovery.md`.
2. Analyze impact and register in `impact-analysis.md`.
3. Plan touched artifacts in `artifact-plan.yaml`.
4. Apply surgical edits to docs, diagrams, models, and operations.
5. Validate via `tools/validators/run_all.py` and platform test suites.
6. Record evidence in `remediation-validation-report.md` and sign off in `review.md`.

## 9. Relationships and Dependencies

- **Upstream Dependencies**:
  - `work-items/DOCS-002-documentation-architecture-reorganization/`
  - `work-items/DATA-001-data-platform-v01-and-microservices/`
- **Downstream Beneficiaries**:
  - All future engineering work items rely on consistent contracts and documentation portals.

## 10. Quality Gate

100% passing rate across all 10 automated documentation validators, 50 platform test cases, and 3 frontend tests with zero broken links and zero ID collisions.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/run_all.py
.\.venv\Scripts\pytest.exe tests -v
npm test --prefix frontend
```

## 12. Agent Restrictions

- Do NOT alter production business logic or runtime algorithms in `src/`.
- Do NOT renumber or delete existing Document IDs, ADR IDs, or Requirement IDs.
- Do NOT introduce unverified external assertions without empirical repository evidence.
