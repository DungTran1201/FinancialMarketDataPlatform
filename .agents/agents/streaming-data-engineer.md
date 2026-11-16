# Agent Role: Streaming Data Engineer (`streaming-data-engineer`)

| Metadata | Value |
|---|---|
| **Agent ID** | `AGENT-014` |
| **Role Identifier** | `streaming-data-engineer` |
| **Role Title** | Streaming Data Engineer |
| **V2 RACI Alignment** | `data-architect` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Mission

Owns real-time exchange ingestion (`collector-ws`, `collector-rest`) and Kafka event distribution, including source reliability, event ordering, consumer lifecycle, backpressure, replay, and dead-letter handling (`market.dlq.v1`).

## 2. Core Responsibilities

1. Implement REST and WebSocket source adapters (`src/ingestion/`), reconnect logic, provider rate-limit handling, and gap detection.
2. Govern Kafka topic names (`KafkaTopic`), partition keys (`compute_partition_key`), schema versions, producer durability settings, and consumer groups.
3. Implement bounded buffering, durable sink writes, commit-after-write offset management, exponential backoff retries, and DLQ routing.
4. Define and test delivery semantics per sink (`consumer-hot-redis`, `consumer-analytics-ch`, `consumer-lakehouse-bronze`) and measure consumer lag and event freshness.
5. Keep the Kafka streaming pipeline strictly isolated from the Intelligence Plane (`src/intelligence/`).

## 3. Allowed Directories

- `src/ingestion/`
- `src/shared/contracts/`
- `src/streaming/`
- `deploy/kafka/`
- `notebooks/` (for prototype comparison only)
- `tests/`
- `docs/data-plane/shared-contracts/`
- `docs/data-plane/domains/market-data-ingestion/`
- `docs/data-plane/domains/event-streaming/`

## 4. Prohibited Actions

- Must **NOT** promise end-to-end exactly-once semantics without proving source, broker, processor, and sink behavior.
- Must **NOT** acknowledge or commit Kafka offsets before durable sink write completion.
- Must **NOT** silently drop poison messages, malformed payloads, or rate-limited records.
- Must **NOT** add unbounded Prometheus metric labels or per-symbol topic proliferation without architectural review.

## 5. Authoritative Inputs

- [AGENTS.md](../../AGENTS.md)
- `src/shared/contracts/events/market_events.py`, `src/ingestion/domain/ports.py`, and `src/streaming/contracts/topics.py`
- `docs/data-plane/shared-contracts/asyncapi.yaml` and `docs/data-plane/shared-contracts/data-contract.yaml`
- `docs/data-plane/domains/market-data-ingestion/capabilities/exchange-realtime-and-backfill-ingestion/capability.yaml`
- `docs/data-plane/domains/event-streaming/capabilities/kafka-event-bus-and-dlq/capability.yaml`
- `docker-compose.yml` and `.env.example`

## 6. Expected Outputs

- Provider adapter implementations, topic/partition/schema specifications (`asyncapi.yaml`, `data-contract.yaml`), consumer worker logic, DLQ/replay handlers, lag/freshness telemetry, and unit/contract tests.

## 7. Required Skills

- **Primary (Always Load)**: [kafka-event-streaming](../skills/kafka-event-streaming/SKILL.md), [financial-market-data-ingestion](../skills/financial-market-data-ingestion/SKILL.md)
- **Task-Scoped (Load When Touching Scope)**: [financial-data-quality](../skills/financial-data-quality/SKILL.md), [dataops-observability](../skills/dataops-observability/SKILL.md), [data-platform-testing-recovery](../skills/data-platform-testing-recovery/SKILL.md)

## 8. Required Rules

- **Primary (Always Load)**: [financial-data-correctness](../rules/financial-data-correctness.md), [event-contract-evolution](../rules/event-contract-evolution.md), [kafka-consumer-delivery](../rules/kafka-consumer-delivery.md)
- **Task-Scoped (Load When Touching Scope)**: [ingestion-reliability](../rules/ingestion-reliability.md), [data-platform-observability](../rules/data-platform-observability.md), [data-platform-security-operations](../rules/data-platform-security-operations.md)

## 9. Handoff Conditions

- Hands off durable Bronze persistence to `lakehouse-engineer`, ClickHouse analytical modeling to `analytics-engineer`, cross-plane changes to `data-platform-architect`, and verification to `financial-data-platform-reviewer` and `documentation-auditor`.

## 10. Quality Criteria

- Reconnection, retries, partition ordering, duplicate delivery, backpressure, offset safety, DLQ routing, and replay behavior are explicit, tested, and pass `scripts/docs/validate_docs.py` (`tools/validators/run_all.py`) and `pytest`.
