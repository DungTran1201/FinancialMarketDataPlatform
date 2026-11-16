---
doc_id: TPL-OPS-OBS-001
title: "Template: Observability & SLO Specification"
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
    - "docs/governance/templates/operations/observability-and-slo.template.md"
related_docs:
  - GOV-STD-NFR-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Created Observability and SLO template enforcing bounded metric cardinality and uninvented target honesty."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Initial V2 Observability and SLO template."
---

# Template: Observability & SLO Specification

Defines SLIs, approved SLOs (or `TARGET_UNRESOLVED`), Prometheus metrics with bounded labels, structured logging, and alerts.

---

# Observability & SLOs: `<Plane or Capability Name>`

## 1. Service Level Indicators (SLIs) & Objectives (SLOs) `[REQUIRED]`

| SLI ID | Indicator Definition | Approved SLO Target (or `TARGET_UNRESOLVED`) | Measurement Window | Current Measured Baseline (`AS-IS`) |
|---|---|---|---|---|
| `SLI-<DOM>-001` | `<Exact metric formula>` | `<Approved target or TARGET_UNRESOLVED [OPEN]>` | `<e.g., rolling 5m>` | `<Measured or NOT_MEASURED>` |

## 2. Prometheus Metrics & Label Cardinality `[REQUIRED]`

| Metric Name | Type (`Counter | Gauge | Histogram`) | Bounded Labels (No high-cardinality IDs) | Source Module |
|---|---|---|---|
| `<metric_name>` | `<Counter>` | `["provider", "status"]` | `<src/...>` |

## 3. Alert Rules & Runbook Links `[REQUIRED]`

| Alert Name | Condition | Severity | Runbook |
|---|---|---|---|
| `<AlertName>` | `<PromQL condition>` | `<warning | critical>` | `[<runbook.md>](<runbook.md>)` |
