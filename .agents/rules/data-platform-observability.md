# Data Rule — Data Platform Observability and SLOs (`DATA-RULE-010`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-010` |
| **Rule Slug** | `data-platform-observability` |
| **Trigger Scope** | Collectors, Kafka, consumers, storage engines, batch jobs, quality suites, APIs, and Agent Tool Gateway |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Governs operational telemetry (Prometheus metrics, structured logs, correlation IDs), bounded metric label cardinality, freshness/lag SLIs, and actionable runbooks across streaming, online-serving, and batch services.

## 2. Mandatory Directives

1. **Core SLIs**: Instrument throughput, error rates, retries, DLQ counts, Kafka consumer lag, data freshness/staleness (`is_stale`), batch duration, sink latency, and quality failures.
2. **Bounded Metric Cardinality**: Keep Prometheus metric labels strictly bounded (`provider`, `event_type`, `status`, `tool_name`); place high-cardinality identifiers (`event_id`, `run_id`, `user_id`, `invocation_id`) in structured logs only.
3. **Workload-Specific SLOs**: Separate online serving (`backend-api`, `redis`), streaming consumers (`collector-ws`, `consumer-*`), and batch jobs (`spark`, `dbt`) when defining latency and freshness targets.
4. **Actionable Alerts & Runbooks**: Pair every alert threshold with an owning role and operator recovery procedure.

## 3. Prohibited Actions

- Do not use `event_id`, `request_id`, `user_id`, or raw payloads as Prometheus metric labels.
- Do not create unowned alerts without documented remediation steps.
- Do not claim runtime SLO compliance without measured telemetry evidence.

## 4. Verification Mechanism

- Prometheus configuration review (`deploy/prometheus/prometheus.yml`), `docs/architecture/11-reliability-and-observability.md`, and `tools/validators/run_all.py`.

