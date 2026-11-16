---
name: phase-gate-review
description: Checklist and execution standard for preparing and verifying Phase Gates (Phases 0-9) and PoC benchmark evidence on greenfield/main.
---

# Phase Gate Review Procedure

1. Verify all deliverables listed for the active phase exist under `docs/` and pass `.\.venv\Scripts\python.exe tools/validators/run_all.py`.
2. Inspect traceability from business requirements -> SRS -> design/ADRs -> work items -> tests -> evidence.
3. For any PoC or performance benchmark (Phase 2, 7, 8):
   - Record exact host hardware specs, Python/OS/container versions, dataset shape, workload rates, duration, raw measurements, and known limitations.
   - Never fabricate or extrapolate unmeasured capacity claims.
4. Record explicit open issues, unresolved conflicts, and blocking prerequisites in the corresponding `docs/phase-reports/` review document before requesting progression approval.
