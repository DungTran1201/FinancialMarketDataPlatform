---
doc_id: GOV-STD-NFR-001
title: "Non-Functional Requirements & Operational Documentation Standards"
doc_type: standard
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
    - "docs/governance/standards/nfr-and-operations-standards.md"
related_docs:
  - GOV-STD-REQ-001
  - GOV-STD-DATA-001
change_metadata:
  approved_by: "Documentation Architect (Phase 1 Foundation)"
  approved_at: "2026-11-16"
  change_summary: "Established the 10-attribute NFR quality model, SLI/SLO definition rules, operational runbook standards, and strict prohibition on invented numerical targets."
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Initial Documentation V2 NFR and operations documentation standard."
---

# Non-Functional Requirements & Operational Documentation Standards

## 1. Common 10-Attribute Quality Model

All Non-Functional Requirements ([nfr.template.md](../templates/product-and-requirements/nfr.template.md)) MUST classify requirements against these 10 quality attributes:

| Quality Attribute | Key Concerns to Specify |
|---|---|
| **1. Performance** | Bounded percentile latency (`P50`/`P95`/`P99`) under explicit workload & payload assumptions |
| **2. Availability** | Service uptime objectives, health/readiness probes, single-point-of-failure disclosures |
| **3. Reliability** | Delivery guarantees (`at-least-once`, idempotency), retry/backoff, DLQ isolation, graceful degradation |
| **4. Scalability** | Horizontal/vertical scaling units, partition counts, rate/row caps, storage growth bounds |
| **5. Security** | AuthN/AuthZ enforcement, TLS versions, secret isolation, audit logging, least-privilege DB roles |
| **6. Maintainability** | Clean dependency boundaries, modularity, schema versioning, deprecation windows |
| **7. Observability** | Bounded-cardinality metrics, structured correlation logs, trace propagation, alerting SLIs |
| **8. Compatibility** | Backward/forward API & event schema evolution, browser/client/protocol support |
| **9. Cost** | Compute/memory budgets, storage TTL/compaction policies, LLM token/iteration caps |
| **10. Recovery** | Backup cadence, RTO/RPO objectives, Kafka replay/backfill procedures, rollback steps |

## 2. Measurable SLI / SLO & Target Integrity Rules

1. **No Invented Operational Targets**: Authors and AI Agents MUST NEVER fabricate `P95`/`P99` latency numbers, throughput rates, availability percentages (`99.9%`), `RTO`, or `RPO` targets.
2. **Unresolved Target Handling**: If a product owner or SRE has not approved a concrete numeric target, the NFR or SLO table MUST record `TARGET_UNRESOLVED` (`[OPEN QUESTION]`) with owner and measurement methodology rather than guessing a plausible figure.
3. **Measured vs. Target Separation**: Observability specs ([observability-and-slo.template.md](../templates/operations/observability-and-slo.template.md)) MUST distinguish approved SLO targets from actual benchmarked measurements (`AS-IS`), citing exact benchmark environment conditions.

## 3. Deployment, Runbook & Incident Recovery Requirements

Risk-proportional operational documentation ([deployment-description.template.md](../templates/operations/deployment-description.template.md), [runbook.template.md](../templates/operations/runbook.template.md), [incident-and-recovery.template.md](../templates/operations/incident-and-recovery.template.md)) MUST include:

- **Deployment**: Exact compose/container profiles, network isolation, port mappings, config env vars (no secrets), and startup order/healthchecks.
- **Monitoring & Alerting**: Metric names, bounded label sets (prohibiting unbounded `event_id`/`user_id` labels), alert condition, severity, and owning role.
- **Incident Response & Runbooks**: Symptom/alert trigger, immediate triage commands, safe mitigation, verification step, and escalation path.
- **Rollback, Backup & Recovery**: Safe rollback steps for failed releases/migrations, backup verification, and destructive-operation approval gates.
