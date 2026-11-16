---
doc_id: TPL-OPS-RB-001
title: "Template: Operational Runbook"
doc_type: template
plane: governance
scope_level: governance
status: APPROVED
implementation_status: NOT_APPLICABLE
version: "2.0.0"
owner_role: devops-sre
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "docs/governance/templates/operations/runbook.template.md"
related_docs:
  - GOV-STD-NFR-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Operational Runbook template for alert-driven triage, safe remediation, and escalation."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Initial V2 Operational Runbook template."
---

# Template: Operational Runbook

Every operational alert MUST link to a concise, executable runbook.

---

# Runbook: `<RB-SCOPE-NNN> — <Alert / Failure Mode>`

## 1. Trigger, Severity & Owning Role `[REQUIRED]`

- **Alert Name / Condition**: `<Metric expression and duration>`
- **Severity**: `<P1 | P2 | P3>`
- **Owner Role**: `devops-sre`

## 2. Triage & Diagnostic Checks `[REQUIRED]`

1. `<Exact read-only log, health endpoint, or metric query>`
2. `<How to distinguish root causes>`

## 3. Safe Remediation & Destructive-Action Guardrails `[REQUIRED]`

- `<Non-destructive mitigation steps>`
- **Destructive Actions** (offset resets, table drops, snapshot expiry): MUST require explicit human operator approval and dry-run check before execution.

## 4. Verification & Escalation `[REQUIRED]`

- **Recovery Verification**: `<Observable metric/status returning to healthy baseline>`
- **Escalation**: `<Owning team/role if unresolved after N minutes>`
