# Implementation Plan: DOCS-003

| Metadata | Value |
|---|---|
| **Work Item ID** | `DOCS-003` |
| **Strategy** | Multi-Phase Non-Disruptive Consistency Remediation |
| **Status** | `IMPLEMENTED` |

---

## 1. Execution Phases

### Phase 0: Baseline & Git Branching
- Establish clean working tree on dedicated branch `docs/DOCS-003-consistency-remediation`.
- Record baseline Git SHA `f0329d3` and snapshot active repository inventory.

### Phase 1: In-Depth Investigation of 14 Historical Points
- Audit `docs/README.md` root traversal.
- Audit `requirements-matrix.md` COMP mappings against `models/architecture/components.yaml`.
- Trace `TokenBucketRateLimiter` code location in `src/ingestion/application/rate_limiter.py`.
- Align JSON envelope in `api-contracts.md` with `EventEnvelopeV1` in `src/shared/contracts/events/market_events.py`.
- Reconcile Diagram 06 topic policies and Diagram 08 pipeline stages against `pipeline.py`.
- Compare `deployment-guide.md` against all 24 services and profiles in `docker-compose.yml`.
- Audit `docs/architecture/README.md` file table for doc 14 and ADR-007..008.
- Scan for Windows absolute paths `file:///c:/...` across all markdown files.

### Phase 2: Technical Consistency Remediation
- Execute surgical edits to `docs/README.md`, `docs/architecture/README.md`, `docs/contracts/requirements-matrix.md`, `docs/contracts/api-contracts.md`, `docs/diagrams/data-platform/06-event-streaming.md`, `docs/diagrams/data-platform/08-end-to-end-data-platform-v01-pipeline.md`, `docs/operations/deployment-guide.md`, `models/data-platform/topics.yaml`, `.agents/config/document-map.yaml`, and `DOCS-002` target documentation tree.

### Phase 3: Work-Item Documentation & Audit Deliverables
- Author all mandatory work-item governance files (`request.md`, `discovery.md`, `impact-analysis.md`, `artifact-plan.yaml`, `implementation-plan.md`, `verification-plan.md`, `review.md`, `state.yaml`, `README.md`).
- Author comprehensive audit registers (`baseline-snapshot.md`, `canonical-source-register.yaml`, `remediation-matrix.csv`, `remediation-matrix.md`, `identifier-audit.md`, `technical-consistency-audit.md`, `diagram-consistency-audit.md`, `documentation-overlap-audit.md`, `link-integrity-audit.md`, `remediation-validation-report.md`).

### Phase 4: Automated Verification & Test Suite Execution
- Run `tools/validators/run_all.py` to ensure 10/10 validators pass with 0 errors.
- Run `pytest tests -v` to ensure 50/50 test cases pass.
- Run `npm test --prefix frontend` to ensure 3/3 frontend tests pass.

### Phase 5: Gate Transitions & Handover
- Advance lifecycle state machine to `DONE`.
- Commit changes with semantic message and deliver comprehensive multi-role audit report.
