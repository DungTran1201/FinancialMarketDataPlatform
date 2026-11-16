---
doc_id: "WI-P2-001"
title: "Phase 2 — Architecture Design, Evaluation Matrix & PoC Work Items"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Principal Software Architect & Performance Engineer"
purpose: "Tracks Phase 2 planning, architecture modeling, PoC isolation environment preparation, and empirical benchmark execution prior to Phase 3."
scope: "Phase 2 Architecture & PoC Execution under DEC-P0-002 (Hybrid Native Windows + Containerized NATS)."
dependencies:
  - "docs/work-items/phase-0-and-1-work-items.md"
  - "docs/product/requirements-traceability-matrix.md"
references:
  - "docs/architecture/README.md"
  - "docs/testing-and-operations/README.md"
assumptions:
  - "Docker Desktop engine can run a single constrained NATS JetStream container cleanly alongside Windows Python 3.12 PoCs."
open_issues:
  - "Docker Desktop currently offline on host; must start & verify memory limit before running NATS benchmark"
review_criteria:
  - "Zero production code written in Phase 2; only isolated PoC scripts & evidence under poc/"
work_items:
  - work_item_id: "WI-P2-001"
    objective: "Author Phase 2 Architecture Package (SAD, Technology Evaluation Matrix, 8 GB Resource Budget, Threat Model, ADRs, Mermaid Diagrams)."
    scope: "All Plane A/B/C structural boundaries, Hybrid PoC topology, failure recovery design, Binance+OKX adapter boundary."
    dependencies: ["WI-P1-001", "WI-P1-002"]
    prerequisites: ["P1-PKG-001 baseline accepted", "OKX selected"]
    steps: ["Complete tech eval matrix", "Design 3-plane 8 GB architecture", "Estimate idle/peak RAM & C: disk budget", "Create threat model & C4/DFD/Deployment diagrams"]
    affected_modules: ["docs/architecture/*", "docs/diagrams/*"]
    test_requirements: ["All architecture docs & Mermaid diagrams pass validate_greenfield.py"]
    acceptance_criteria: ["All Section 7 Phase 2 design deliverables present and traceable to RTM"]
    risks: ["Underestimating Windows Docker/WSL2 RAM usage"]
    evidence: ["docs/architecture/system-architecture-document.md", "docs/architecture/technology-evaluation-matrix.md", "docs/architecture/resource-budget.md", "docs/architecture/threat-model.md", "docs/diagrams/*"]
    status: "IN_REVIEW"
  - work_item_id: "WI-P2-002"
    objective: "Define Benchmark Plan & Measurable Acceptance Criteria covering all 12 Section 6 dimensions + Binance/OKX API probe."
    scope: "NATS JetStream throughput/latency/restart/replay, cache, SQLite WAL, DuckDB+Parquet, combined RSS/CPU/disk I/O."
    dependencies: ["WI-P2-001"]
    prerequisites: ["Architecture topology documented"]
    steps: ["Define datasets & burst profiles", "Define measurement scripts using psutil & timing histograms", "Specify raw artifact output format & limitation disclosures"]
    affected_modules: ["docs/testing-and-operations/phase-2-poc-benchmark-plan.md", "poc/*"]
    test_requirements: ["Reproducible PoC runner scripts"]
    acceptance_criteria: ["All 12 required Phase 2 criteria mapped to executable probes"]
    risks: ["Docker engine unavailability on host blocking containerized NATS check"]
    evidence: ["docs/testing-and-operations/phase-2-poc-benchmark-plan.md", "poc/README.md", "poc/docker-compose.nats.yml"]
    status: "IN_REVIEW"
  - work_item_id: "WI-P2-003"
    objective: "Prepare isolated Python 3.12 PoC environment & run isolated NATS/DuckDB/Polars/SQLite/Binance+OKX capability PoCs."
    scope: "Rebuilt slim .venv [poc], NATS Docker Compose config, PoC benchmark runs, and empirical Phase 2 Evidence Report."
    dependencies: ["WI-P2-002"]
    prerequisites: ["Docker Desktop running for NATS JetStream test; internet access for Binance/OKX public REST/WS capability check"]
    steps: ["Rebuild slim .venv with poc deps", "Run POC-02/03/05 locally", "Start Docker Desktop w/ .wslconfig cap and run POC-01 & POC-04", "Finalize Phase 2 ADRs"]
    affected_modules: ["poc/*", "docs/testing-and-operations/phase-2-poc-results.md"]
    test_requirements: ["Automated PoC harness executions with crash/restart verification"]
    acceptance_criteria: ["All 5 PoCs (POC-01..POC-05) satisfy NFR targets on 7.85 GB host with raw JSON evidence"]
    risks: ["Docker Desktop stopped on host (com.docker.service=Stopped) and 1.55 GB free host RAM without .wslconfig limit"]
    evidence: ["POC-02 PASS (poc_02_cache_sqlite.json)", "POC-03 DuckDB PASS (poc_03_analytics_parquet.json)", "POC-05 Binance+OKX LIVE PASS (poc_05_exchanges.json)", "POC-01 & POC-04 BLOCKED pending Docker Engine startup"]
    status: "BLOCKED"
---

# Phase 2 Work Items (`WI-P2-001` .. `WI-P2-003`)

- `WI-P2-001` & `WI-P2-002`: **IN_REVIEW** (Architecture Package, Diagrams, Benchmark Plan & isolated PoC scripts complete and validated).
- `WI-P2-003`: **BLOCKED (`BLOCKER-P2-DOCKER`)** — Local Python/DuckDB/SQLite/Exchange probes (`POC-02`, `POC-03`, `POC-05`) executed cleanly with raw JSON evidence in [phase-2-poc-results.md](../testing-and-operations/phase-2-poc-results.md); **containerized NATS JetStream (`POC-01`, `POC-04`) awaits starting Docker Desktop safely** (`com.docker.service` currently `Stopped`, `1.55 GB` free RAM, no `.wslconfig` memory ceiling configured).
