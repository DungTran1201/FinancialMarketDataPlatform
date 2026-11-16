---
doc_id: "WI-P01-001"
title: "Phase 0 & Phase 1 Work Items Register"
version: "1.0.0"
status: "ACCEPTED"
implementation_status: "VERIFIED"
owner: "System Analyst & Product Manager"
purpose: "Formal Section 9 tracking for Phase 0 Discovery, Phase 1 Requirements Baseline, and Orphan Repo Preparation."
scope: "Phases 0 and 1 execution on greenfield/main."
dependencies:
  - ".agents/workflows/phase-lifecycle.md"
  - "docs/phase-reports/phase-1-acceptance-and-decisions.md"
references:
  - "docs/product/requirements-traceability-matrix.md"
assumptions: []
open_issues: []
review_criteria:
  - "Every completed item lists verifiable evidence"
work_items:
  - work_item_id: "WI-P0-001"
    objective: "Inspect repository baseline, host hardware (RAM/CPU/disk/WSL), installed tooling, and legacy conventions."
    scope: "Phase 0 discovery across host and git repo without mutating files."
    dependencies: []
    prerequisites: ["Workspace access"]
    steps: ["Inspect git status/branches", "Measure Windows RAM/CPU/disk/WSL/Docker/Python/Node", "Produce 10 Phase 0 deliverables"]
    affected_modules: ["docs/phase-reports/phase-0-discovery-report.md"]
    test_requirements: ["Reproducible host telemetry script output"]
    acceptance_criteria: ["All 10 Phase 0 deliverables recorded with real host numbers"]
    risks: ["Misstating 8 GB hardware constraints"]
    evidence: ["docs/phase-reports/phase-0-discovery-report.md (7.85 GB RAM, i5-12400F, 15.54 GB free C:)"]
    status: "COMPLETE"
  - work_item_id: "WI-P1-001"
    objective: "Define and version Phase 1 Vision, SRS, Use Cases, RTM, Acceptance Criteria, Glossary, Roadmap, and Conflict Audit."
    scope: "Complete functional/NFR/8 GB/multi-asset specification across Data, Intelligence, and Application planes."
    dependencies: ["WI-P0-001"]
    prerequisites: ["Phase 0 accepted & DEC-P0-001/DEC-P0-002/OPEN-P1-002 decisions issued"]
    steps: ["Author versioned specs", "Resolve 6 RTM pre-Phase 2 conflicts/missing ACs", "Validate via run_all.py"]
    affected_modules: ["docs/product/*"]
    test_requirements: ["Greenfield doc & RTM validator pass"]
    acceptance_criteria: ["P1-PKG-001 8 conditions satisfied; RTM conflict audit documented"]
    risks: ["Ambiguous flow/contract definitions causing Phase 2 rework"]
    evidence: ["docs/product/requirements-traceability-matrix.md", "docs/phase-reports/phase-1-acceptance-and-decisions.md"]
    status: "COMPLETE"
  - work_item_id: "WI-P1-002"
    objective: "Initialize clean orphan branch greenfield/main preserving legacy branches and rebuild .agents + greenfield validator."
    scope: "Git orphan branch creation, legacy folder cleanup, new validator replacing incompatible V2 validator."
    dependencies: ["WI-P0-001"]
    prerequisites: ["DEC-P0-001 explicit authorization"]
    steps: ["Verify legacy branch integrity", "git checkout --orphan greenfield/main", "Inspect V2 validator", "Build validate_greenfield.py & .agents/hooks.json"]
    affected_modules: [".agents/*", "tools/*", "AGENTS.md", "README.md", "pyproject.toml", ".gitignore"]
    test_requirements: ["git log on legacy branches intact; greenfield validator passes 0 errors"]
    acceptance_criteria: ["Zero mixed legacy files on greenfield/main; PostToolUse validation active"]
    risks: ["Accidental deletion of legacy branches or disabling validation"]
    evidence: ["Orphan greenfield/main active; legacy main (f0329d3) & feat/data-plane-production-delivery (e7708e0) preserved; legacy bloat removed (.venv shrunk 1400.9 -> 337.5 MB); validate_greenfield.py & ruff pass 0 errors"]
    status: "COMPLETE"
---

# Phase 0 & Phase 1 Work Items (`WI-P0-001`, `WI-P1-001`, `WI-P1-002`)

Track status updates rigorously per [docs/work-items/README.md](README.md) (`BACKLOG` $\rightarrow$ `COMPLETE`).
- `WI-P0-001`: **COMPLETE** — Verified Phase 0 baseline recorded in [phase-0-discovery-report.md](../phase-reports/phase-0-discovery-report.md).
- `WI-P1-001`: **COMPLETE** — Versioned Phase 1 baseline (`v1.0.0`) committed under [docs/product/](../product/README.md) with all 6 pre-Phase 2 conflicts/missing ACs resolved in [requirements-traceability-matrix.md](../product/requirements-traceability-matrix.md).
- `WI-P1-002`: **COMPLETE** — Clean orphan branch `greenfield/main`, slim Python `3.12` `.venv` (`337.49 MB`), rebuilt `.agents/`, `validate_greenfield.py`, and `ruff` verified with `0` errors.
