# Work Item `DOCS-004`: Full Documentation Remediation, Architecture Reconciliation & Governance Acceptance

## 1. Directory Purpose

Tracks the repository-wide documentation remediation program across Workstreams A–D: completion of `DOCS-003` technical consistency, Architecture Baseline Reconciliation (`ARCH`), Operations Verification (`OPS`), and Documentation Governance Consolidation (`DOCS`), concluding with independent Final Acceptance verification.

## 2. Scope and Boundaries

- **Belongs in this directory**: `DOCS-004` intake, baseline snapshot, canonical source register, discovery and impact analysis, artifact plan, implementation/verification plans, remediation/traceability/consolidation matrices, independent review, final acceptance report, and lifecycle state machine (`state.yaml`).
- **Does NOT belong in this directory**: Direct edits to runtime business logic under `src/` or `frontend/`. Any runtime/frontend defects discovered are documented as separate engineering proposals in `discovery.md` and `final-acceptance-report.md`.

## 3. Agent Role and Responsibilities

- **Program Ownership**: `documentation-architect`, `data-platform-architect`, `api-architect`, `dataops-engineer`, `documentation-auditor`, and `qa-reviewer`.

## 4. Authoritative Inputs

1. Verified runtime codebase under `src/`, `frontend/src/`, `deploy/`, `docker-compose.yml`, `.env.example`, and `tests/`.
2. Canonical YAML models under `models/`.
3. Governance configs and validators under `.agents/` and `tools/validators/`.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Work item navigation and governance contract | Required | `work-items/_template/README.md` |
| `request.md` | Remediation program scope and non-negotiable constraints | Required | `work-items/_template/request.md` |
| `baseline-snapshot.md` | Immutable pre-edit Git, test, validator, and inventory capture | Required | Program baseline artifact |
| `canonical-source-register.yaml` | Authoritative code/config/model source registry | Required | Program baseline artifact |
| `document-inventory.csv` | Complete markdown/model/diagram/config classification register | Required | Program inventory artifact |
| `discovery.md` | Fact-classified audit (`FACT`, `ASSUMPTION`, `DECISION`, `OPEN QUESTION`) + runtime engineering proposals | Required | `work-items/_template/discovery.md` |
| `impact-analysis.md` | Cross-subsystem inconsistency impact and remediation risk matrix | Required | `work-items/_template/impact-analysis.md` |
| `artifact-plan.yaml` | Machine-readable list of planned artifact actions | Required | `work-items/_template/artifact-plan.yaml` |
| `implementation-plan.md` | Sequenced execution plan (`models/` -> `compose` -> `docs/` -> `diagrams/` -> `validators/`) | Required | `work-items/_template/implementation-plan.md` |
| `verification-plan.md` | Independent test, validator, Compose, and negative-test plan | Required | `work-items/_template/verification-plan.md` |
| `review.md` | Independent quality review and acceptance sign-off | Required | `work-items/_template/review.md` |
| `state.yaml` | Lifecycle state machine (`INTAKE` through `DONE`) | Required | `work-items/_template/state.yaml` |

## 6. Directory and File Organization

Flat work-item folder under `work-items/DOCS-004-full-documentation-remediation/` using clean ASCII/UTF-8 tables and YAML/CSV registers.

## 7. Document Creation Rules

- Preserve every existing identifier (`FR-*`, `ADR-*`, `COMP-*`, `DOM-*`, `API-*`, `TC-*`, `DIAG-*`).
- Distinguish `IMPLEMENTED`, `PARTIALLY_IMPLEMENTED`, `PLANNED`, `DEPRECATED`, `SUPERSEDED`, `ARCHIVED`, `UNVERIFIED`.
- Distinguish `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED`, `UNVERIFIED`.

## 8. Creation Workflow

1. Capture clean baseline (`G0_DISCOVERY`) before editing any governed artifact.
2. Update `.agents/config/` and `models/**/*.yaml` first.
3. Reconcile `docker-compose.yml`/`.env.example` minimal port collision configuration defect and regression-test.
4. Reconcile all `docs/**` and `.agents/**`, then `docs/diagrams/**` and historical `DOCS-002`/`DOCS-003` addenda.
5. Upgrade `tools/validators/` + isolated negative tests, execute full independent verification (`G4`/`G6`), and publish Final Acceptance.

## 9. Relationships and Dependencies

Continues and supersedes incomplete claims in `DOCS-002` and `DOCS-003`; references `ARCH-001`, `DATA-001`, `FEAT-001`, `FEAT-002`, and `DOCS-001`.

## 10. Quality Gate

`tools/validators/run_all.py` (with upgraded semantic checks), `pytest tests -v`, `ruff check`, `npm test`/`npm run build --prefix frontend`, and `docker compose --profile ... config` must all pass after the final edit with evidence recorded verbatim in `final-acceptance-report.md`.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/run_all.py
.\.venv\Scripts\pytest.exe tests -v
```

## 12. Agent Restrictions

- Do NOT modify `src/` or `frontend/` runtime business logic under `DOCS-004`.
- Do NOT mark unrun tests or unverified claims as `PASS` or `APPROVED`.

