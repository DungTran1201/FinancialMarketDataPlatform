# Phase Lifecycle & Work-Item Workflow

## Phase Gates (`Phase 0` -> `Phase 9`)
- **Phase 0**: Discovery, Environment & Hardware Baseline $\rightarrow$ User Acceptance.
- **Phase 1**: Vision, SRS, Multi-Asset Use Cases, RTM, Acceptance Criteria, Roadmap $\rightarrow$ Versioned Baseline.
- **Phase 2**: Architecture Design (SAD, ADRs, Diagrams, 8 GB Resource Budget, Threat Model) + Benchmark Plan $\rightarrow$ **Isolated Technology PoCs** $\rightarrow$ Phase 2 Gate Review.
- **Phase 3**: Canonical Schemas, Event/API/Feature Contracts & Contract Tests.
- **Phase 4**: Data Plane Implementation (stepwise by dependency order).
- **Phase 5**: Intelligence Plane Implementation (datasets $\rightarrow$ features $\rightarrow$ Tier 0/1/2 models $\rightarrow$ walk-forward eval $\rightarrow$ online inference).
- **Phase 6**: Application Plane Implementation (real backend-backed 15-module SPA).
- **Phase 7**: System Integration, Chaos Replay & Resource Tests.
- **Phase 8**: Deployment Profiles, Backup/Restore Drills & Soak Validation.
- **Phase 9**: Formal Production Readiness Review.

## Work Item Lifecycle Rules
Track every implementation/design unit under [docs/work-items/](../../docs/work-items/README.md) with states:
`BACKLOG -> READY -> IN_PROGRESS -> (BLOCKED) -> IN_REVIEW -> TESTING -> ACCEPTED -> COMPLETE`
Never transition an item to `COMPLETE` without explicit verified test/measurement `evidence`.
