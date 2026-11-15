# Implementation Plan: Documentation Architecture Reorganization (`DOCS-002`)

| Metadata | Value |
|---|---|
| **Work Item ID** | `DOCS-002` |
| **Stage** | `PLAN_REVIEW` |
| **Risk Tier** | `R2` |
| **Updated Date** | `2026-11-15` |
| **Owning Agent Role** | `documentation-architect` |

---

## 1. Phased Execution Sequence

### Phase 1: Repository Documentation Audit
- Complete automated inventory scan of 186 Markdown files and 38 YAML models.
- Build full incoming/outgoing link graph across repository.
- Detect broken links and verify implementation reality vs documentation.

### Phase 2: Build Documentation Migration Matrix
- Author `documentation-migration-matrix.csv` with mandatory 18-column schema.
- Author `documentation-migration-matrix.md` with classification summaries and rationales.
- Categorize every artifact into `KEEP`, `MOVE`, `MERGE`, `UPDATE`, `ARCHIVE`, `SPLIT`, or `REFERENCE_ONLY`.

### Phase 3: Design Target Documentation Architecture
- Author `target-documentation-tree.md` establishing the 9-domain Reader Journey framework.
- Define boundaries for `overview/`, `architecture/`, `contracts/`, `diagrams/`, `operations/`, `development/`, `product/`, `templates/`, and `archive/`.

### Phase 4: Diagram Consolidation
- Audit all 22 technical Mermaid diagrams in `docs/diagrams/`.
- Verify the 8 core master architectural views against canonical models.
- Author `diagram-migration-report.md`.

### Phase 5: Documentation Migration Execution
- Author new domain directories:
  - `docs/overview/` (`README.md`, `system-overview.md`, `technology-stack.md`)
  - `docs/contracts/` (`README.md`, `requirements-matrix.md`, `api-contracts.md`)
  - `docs/operations/` (`README.md`, `deployment-guide.md`, `operational-runbooks.md`)
  - `docs/development/` (`README.md`, `developer-quickstart.md`, `codebase-map.md`)
  - `docs/archive/` (`README.md`, `historical-notes.md`)
- Ensure every new directory contains a fully compliant 12-section `README.md`.
- Update `docs/README.md` to serve as the unified Reader Journey navigation portal.
- Update `.agents/config/document-map.yaml` to register new domain paths.
- Fix all detected broken cross-links in existing baseline documents.

### Phase 6: Integrity & Traceability Validation
- Author `identifier-integrity-report.md` (237 IDs verified).
- Author `document-reference-audit.md` (367 links verified, 0 broken).
- Execute `tools/validators/run_all.py` (all 10 validators pass).
- Execute `pytest tests/ -v` (all 50 tests pass).
- Execute `npm test --prefix frontend` (3/3 tests pass).
- Record final audit sign-off in `review.md` and `migration-validation-report.md`.

