---
name: dataops-observability
description: Streaming/batch SLIs, lag/freshness alerts, Prometheus telemetry, and operational runbooks.
---

# Skill: DataOps, Observability & Recovery Operations (`SKILL-021`)

## 1. Description

Operate streaming and batch data services with actionable SLIs, bounded-cardinality Prometheus telemetry, freshness/lag alerts, Docker Compose health checks, and recovery runbooks.

## 2. Trigger Conditions

- Metrics/logs/traces, Kafka consumer lag, data freshness, alert rules, Docker Compose profiles, health checks, backup/restore, or recovery runbooks (`dataops-engineer`, `devops-sre`).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/governance/standards/nfr-and-operations-standards.md`, `docs/data-plane/architecture/observability-and-monitoring.md`, `docs/<plane>/operations/{runbook.md,observability-and-slo.md,incident-and-recovery.md}`, `docker-compose.yml`, `.env.example`, `deploy/observability/prometheus/prometheus.yml`, `src/shared/config/settings.py`, `src/shared/observability/metrics.py`.

## 4. Preconditions

1. Owning Plane operations docs and `capability.yaml` read; workload class (`online-serving`, `streaming`, `batch`), owning role, critical signals, and alert response actions identified.

## 5. Execution Procedure

1. Define SLIs for throughput, error rate, latency, Kafka consumer lag, data freshness, batch duration, quality failures, and recovery duration without inventing unconfirmed SLO targets.
2. Instrument counters, gauges, and histograms with stable units and bounded labels (`provider`, `event_type`, `status`, `tool_name`).
3. Use structured logs with correlation context (`run_id`, `event_id`, `invocation_id`); never place high-cardinality IDs in Prometheus labels.
4. Define alert thresholds, evaluation windows, severity, owning role, and operator runbooks under `docs/<plane>/operations/` or `<capability>/operations/`.
5. Keep `docker-compose.yml` profiles and container health checks aligned with actual service dependencies and resource budgets.
6. Document backup, restore, Kafka replay, DLQ reprocessing, lakehouse backfill, and table-maintenance procedures.
7. Run `scripts/docs/validate_docs.py` and observability tests.

## 6. Output Artifacts

- Prometheus configuration (`deploy/observability/prometheus/`), Docker Compose profile updates (`docker-compose.yml`), operational runbooks/SLOs/recovery docs (`docs/<plane>/operations/`), and observability capability specs.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/integration/test_realtime_observability_dashboard.py -v
```

## 8. Failure Handling

- Escalate operator ownership when data loss, freshness breaches, or recovery uncertainty exists; never execute destructive remediation without human approval.

## 9. Restrictions

- No secrets in logs or VCS.
- No unbounded Prometheus metric labels.
- No unapproved Kubernetes or service-mesh additions.
- No unmeasured claims of runtime SLO compliance.

## 10. Related Skills

- `kafka-event-streaming`
- `lakehouse-medallion`
- `data-platform-testing-recovery`
- `data-governance-lineage`
