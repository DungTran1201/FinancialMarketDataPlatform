# Work Item: Documentation Architecture Reorganization (`DOCS-002`)

## 1. Directory Purpose

`work-items/DOCS-002-documentation-architecture-reorganization/` governs the complete audit, classification, standardization, and architectural reorganization of the **FinancialMarketDataPlatform** documentation subsystem. It transitions the documentation repository into an **Engineering Domain & Reader-Journey** centric framework while strictly enforcing 100% backward compatibility, zero renumbered identifiers, and zero broken links.

## 2. Scope and Boundaries

- **In Scope**:
  - Full audit of 186 Markdown documents in `docs/` and all canonical YAML models in `models/`.
  - Generation of the comprehensive Documentation Migration Matrix (`documentation-migration-matrix.csv` and `.md`).
  - Establishment of Domain and Reader Journey entry portals (`docs/overview/`, `docs/contracts/`, `docs/operations/`, `docs/development/`, `docs/archive/`).
  - Diagram consolidation and synchronization of all 22 technical Mermaid diagrams with canonical models.
  - Link integrity and identifier integrity verification.
  - Synchronization of root `README.md`, `docs/README.md`, `AGENTS.md`, and `.agents/config/document-map.yaml`.
- **Out of Scope**:
  - Altering canonical YAML models in `models/` without architectural justification.
  - Renumbering any baseline identifiers (`ADR-*`, `FR-*`, `DIAG-*`, `COMP-*`, etc.).
  - Deleting baseline files required by `tools/validators/validate_docs.py`.

## 3. Agent Role and Responsibilities

- **Lead Agent Role**: `documentation-architect` (Senior Documentation Architect & Migration Engineer).
- **Collaborating Roles**: `discovery-analyst`, `data-platform-architect`, `documentation-auditor`.
- **Responsibilities**:
  - Conduct deep inventory audit and classify all artifacts.
  - Author domain portals, navigation guides, and audit reports.
  - Resolve detected link inconsistencies and verify all validators pass with zero errors.

## 4. Authoritative Inputs

1. [AGENTS.md](../../AGENTS.md) — Root Agent Operating System & Documentation Contract.
2. [.agents/config/document-map.yaml](../../.agents/config/document-map.yaml) — System Documentation Map.
3. [.agents/config/identifier-registry.yaml](../../.agents/config/identifier-registry.yaml) — Identifier Registry & Preservation Policy.
4. [.agents/config/artifact-matrix.yaml](../../.agents/config/artifact-matrix.yaml) — Artifact Selection Matrix.
5. [.agents/config/phase-gates.yaml](../../.agents/config/phase-gates.yaml) — Gate Exit Criteria.

## 5. Required Artifacts

| Artifact | Purpose | Required / Conditional | Template |
|---|---|---|---|
| `README.md` | Work item directory overview and index | Required | `work-items/_template/README.md` |
| `request.md` | Intake request, objectives, and constraints | Required | `work-items/_template/request.md` |
| `discovery.md` | Repository audit findings, fact register, and conflict analysis | Required | `work-items/_template/discovery.md` |
| `impact-analysis.md` | Cross-subsystem impact analysis and risk evaluation | Required | `work-items/_template/impact-analysis.md` |
| `artifact-plan.yaml` | Machine-readable artifact plan | Required | `work-items/_template/artifact-plan.yaml` |
| `implementation-plan.md` | 6-Phase staged execution plan | Required | `work-items/_template/implementation-plan.md` |
| `verification-plan.md` | Verification protocol and validator execution plan | Required | `work-items/_template/verification-plan.md` |
| `review.md` | Final audit review and sign-off record | Required | `work-items/_template/review.md` |
| `state.yaml` | Work item state machine | Required | `work-items/_template/state.yaml` |
| `documentation-migration-matrix.csv` | Machine-readable 186-artifact migration register | Required | `work-items/_template/artifact-plan.yaml` |
| `documentation-migration-matrix.md` | Human-readable migration matrix | Required | `docs/templates/governance/governance.template.md` |
| `target-documentation-tree.md` | Target directory architecture and reader journey | Required | `docs/templates/architecture/architecture-overview.template.md` |
| `document-reference-audit.md` | Complete link and reference audit report | Required | `docs/templates/governance/governance.template.md` |
| `identifier-integrity-report.md` | ID preservation and collision analysis | Required | `docs/templates/governance/governance.template.md` |
| `diagram-migration-report.md` | 22-diagram consolidation and mapping report | Required | `docs/templates/diagrams/architecture-diagram.template.md` |
| `migration-validation-report.md` | Quality gates and validation evidence report | Required | `docs/templates/testing/test-plan.template.md` |

## 6. Directory and File Organization

All 16 governing artifacts sit inside `work-items/DOCS-002-documentation-architecture-reorganization/`.

## 7. Document Creation Rules

- All artifacts follow standardized templates and strict metadata headers.
- Fact discipline enforced: All statements verified against codebase or approved models.
- Valid lifecycle state progression: `INTAKE → DISCOVERY → IMPACT → DESIGN → PLAN_REVIEW → IMPLEMENT → VERIFY → SYNC → RELEASE → DONE`.

## 8. Creation Workflow

1. Perform inventory audit across repository and generate CSV/Markdown matrix.
2. Establish target architecture and verify backward compatibility.
3. Create new domain portals and 12-section READMEs.
4. Resolve broken links and verify references.
5. Execute validation suite `tools/validators/run_all.py` and unit tests.
6. Record audit findings in `review.md` and complete gate sign-off.

## 9. Relationships and Dependencies

- **Upstream**: Root documentation governance in `AGENTS.md` and `docs/README.md`.
- **Downstream**: Directs all documentation portals in `docs/` and configurations in `.agents/config/`.

## 10. Quality Gate

- All 16 artifacts created and populated.
- Zero broken links (367/367 valid).
- 100% identifier preservation across 21 namespaces.
- All 10 validators in `tools/validators/run_all.py` pass with 0 errors.

## 11. Validation Commands

```powershell
.\.venv\Scripts\python.exe tools/validators/run_all.py
.\.venv\Scripts\pytest.exe tests -v
```

## 12. Agent Restrictions

- **Do NOT** delete any preserved baseline file required by `validate_docs.py`.
- **Do NOT** renumber or mutate existing identifiers (`ADR-*`, `FR-*`, `DIAG-*`, etc.).
- **Do NOT** create directories without compliant 12-section `README.md` files.
