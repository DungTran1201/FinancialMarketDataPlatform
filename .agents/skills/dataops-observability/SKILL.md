---
name: dataops-observability
description: "Operate streaming and batch data services with actionable metrics, bounded-cardinality telemetry, freshness/lag alerts, runbooks and recovery tests."
---

# Skill: DataOps, Observability & Recovery Operations (`SKILL-021`)

## 1. Description

Operate streaming and batch data services with actionable metrics, bounded-cardinality telemetry, freshness/lag alerts, runbooks, and recovery tests.

## 2. Trigger Conditions

- Use for metrics/logs/traces, Kafka consumer lag, data freshness, alert rules, Docker Compose profiles, service health checks, backup/restore, recovery procedures, and incidents.
- Invoked by Agent role `dataops-engineer` (`.agents/agents/dataops-engineer.md`).

## 3. Authoritative Inputs

- `AGENTS.md` and target directory `README.md`
- `docs/architecture/11-reliability-and-observability.md` and `12-deployment-architecture.md`
- `docker-compose.yml`, `.env.example`, `deploy/prometheus/prometheus.yml`, and `src/shared/config.py`
- `models/deployment/deployment.yaml`

## 4. Preconditions

1. Target directory `README.md` has been read in full.
2. Component workload class (`online-serving`, `streaming`, or `batch`), owning role, critical signals, and alert response actions have been identified.

## 5. Execution Procedure

1. Define SLIs for throughput, error rate, latency, Kafka consumer lag, data freshness, batch duration, quality failures, and recovery duration.
2. Instrument counters, gauges, and histograms with stable units and bounded labels (`provider`, `event_type`, `status`, `tool_name`).
3. Use structured logs with correlation context (`run_id`, `event_id`, `invocation_id`); never place high-cardinality IDs in Prometheus labels.
4. Define alert thresholds, evaluation windows, severity, owning role, and operator runbooks (`docs/product/13-operations/`).
5. Keep `docker-compose.yml` profiles and container health checks aligned with actual service dependencies and resource budgets.
6. Document backup, restore, Kafka replay, DLQ reprocessing, lakehouse backfill, and table-maintenance procedures.
7. Synchronize `models/deployment/deployment.yaml` and run `tools/validators/run_all.py`.

## 6. Output Artifacts

- Prometheus configuration (`deploy/prometheus/`), Docker Compose profile updates (`docker-compose.yml`), operational runbooks (`docs/product/13-operations/`), and updated deployment models (`models/deployment/`).

## 7. Validation

```powershell
python tools/validators/run_all.py
python -m unittest discover -s tests -v
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

