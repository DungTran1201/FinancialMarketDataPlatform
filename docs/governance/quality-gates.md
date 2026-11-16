---
doc_id: GOV-POL-GATE-001
title: "Documentation Lifecycle Quality Gates"
doc_type: governance
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: documentation-tooling-engineer
accountable_role: documentation-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/quality-gates.md"
related_docs:
  - GOV-POL-LIFE-001
  - GOV-POL-REV-001
  - GOV-POL-DOD-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established mandatory automated and human review gates across the 9-stage documentation lifecycle."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: documentation-tooling-engineer
    summary: "Initial Documentation V2 quality gates specification."
---

# Documentation Lifecycle Quality Gates

Each gate MUST pass before advancing a capability or specification to the next lifecycle stage.

| Gate ID | Lifecycle Boundary | Mandatory Checks (Automated + Human) | Blocking Authority |
|---|---|---|---|
| `QG-1-SCOPE` | Stage 1 -> Stage 2 | `capability.yaml` conforms to `capability-manifest.schema.json`; risk tier & signals set; `AS-IS` facts separated from unknowns | `business-analyst` |
| `QG-2-REQS` | Stage 2 -> Stage 3 | Unique requirement IDs; atomic/verifiable wording; missing thresholds/decisions marked `OPEN`/`BLOCKED`; zero invented targets | `business-analyst` |
| `QG-3-SPEC-DESIGN` | Stage 3/4 -> Stage 5 | All applicable artifacts per `artifact-applicability-matrix.yaml` populated; OpenAPI/AsyncAPI/Data Contracts valid; `NOT_APPLICABLE` reasons recorded; `AS-IS` vs `TARGET` separated | `system-architect` / `data-architect` |
| `QG-4-SECURITY` | Stage 4 -> Stage 5 (`MEDIUM` auth / `HIGH_CRITICAL`) | Threat model covers all 9 mandatory elements; authorization matrix complete; zero hardcoded secrets; insecure `AS-IS` gaps flagged honestly | `security-architect` |
| `QG-5-APPROVAL` | Stage 5 -> Stage 6 | `scripts/docs/validate_docs.py` exits `0`; zero `TBD`/`TODO`; `change_metadata` complete; required RACI approvals obtained | Accountable Owner (`roles-and-raci.md`) |
| `QG-6-VERIFY` | Stage 6 -> Stage 7/8 | Code matches contracts; `TC` suites executed with explicit test environment disclosure; `implementation_status` reflects true state | `qa-lead` |
| `QG-7-OPS` | Stage 8 (Release) | Deployment descriptor, bounded-label observability, SLI/SLO checks, and runbook/recovery procedures reviewed | `devops-sre` |

## Automated Enforcement Command

```powershell
.\.venv\Scripts\python.exe scripts/docs/validate_docs.py
```

Any exit code other than `0` MUST block merge on documentation pull requests.
