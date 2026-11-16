---
doc_id: "DOC-OPS-ROOT"
title: "Testing, Benchmarks & Operations Index"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Principal QA Engineer, Performance Engineer & SRE"
purpose: "Central location for Phase 2 PoC benchmark plans/evidence, test strategies, security test plans, runbooks, backup/restore, and monitoring alerts."
scope: "Verification, benchmarking, resilience drills, and single-node 8 GB operations."
dependencies:
  - "docs/product/acceptance-criteria.md"
  - "docs/architecture/README.md"
references:
  - "docs/work-items/README.md"
assumptions:
  - "Phase 2 benchmarks execute against real local processes and containerized NATS JetStream on Windows 10 host."
open_issues:
  - "Actual PoC measurements will populate evidence docs after Phase 2 benchmark execution."
review_criteria:
  - "Includes hardware profile, raw numbers, reproducibility instructions, and limitations"
---

# Testing & Operations (`docs/testing-and-operations/`)

Maintains test strategies, measurable Phase 2 PoC benchmark workloads and raw evidence reports, runbooks, backup/restore drills, and observability specifications.

