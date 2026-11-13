---
name: financial-market-data-ingestion
description: "Build resilient financial exchange REST and WebSocket ingestion with canonical normalization, exact precision, rate-limit handling and replayable watermarks."
---

# Skill: Resilient Financial Exchange Ingestion (`SKILL-023`)

## 1. Description

Build resilient financial exchange REST and WebSocket ingestion with canonical normalization, exact `Decimal` precision, rate-limit handling, and replayable watermarks.

## 2. Trigger Conditions

- Use when adding or updating exchange providers, REST pagination (`collector-rest`), WebSocket streams (`collector-ws`), gap recovery, provider metadata discovery, or collector behavior.
- Invoked by Agent roles `streaming-data-engineer` and `data-engineer`.

## 3. Authoritative Inputs

- `AGENTS.md` and target directory `README.md`
- `src/collectors/ports.py`, `src/collectors/main_ws.py`, `src/collectors/main_rest.py`, and `src/shared/contracts/events.py`
- `docs/specifications/data-contracts.md` and `docs/architecture/04-data-platform-architecture.md`
- `.env.example` and `deploy/postgres/init/01_schema.sql` (`ingestion_watermarks`)

## 4. Preconditions

1. Target directory `README.md` has been read in full.
2. Provider, event type, natural key, UTC timestamp source, deterministic UUIDv5 identity (`compute_deterministic_event_id`), target Kafka topic, and partition ordering key (`compute_partition_key`) have been defined.

## 5. Execution Procedure

1. Isolate provider-specific transport and payload parsing behind collector ports (`src/collectors/ports.py`).
2. Normalize symbols, event types, units, and exact `Decimal` values into `EventEnvelopeV1` (`MarketTradePayloadV1`, `MarketKlinePayloadV1`).
3. Preserve raw source payload and metadata for diagnosis and replay.
4. Implement bounded REST pagination with explicit page boundaries, `HTTP 429` / `418` rate-limit parsing, exponential backoff with jitter, and idempotent resume.
5. Implement WebSocket lifecycle: subscription, heartbeat, reconnect, resubscribe, graceful shutdown, and sequence gap detection.
6. Advance `ingestion_watermarks` in PostgreSQL only after the designated durable sink has accepted the batch.
7. Route validation failures to `market.dlq.v1` (`DeadLetterEnvelopeV1`) while keeping the collector process healthy.
8. Add unit/contract tests in `tests/` and run `tools/validators/run_all.py`.

## 6. Output Artifacts

- Provider collector adapters (`src/collectors/`), normalization contract tests (`tests/`), updated data contracts (`docs/specifications/data-contracts.md`), and ingestion runbook notes.

## 7. Validation

```powershell
python tools/validators/run_all.py
python -m unittest discover -s tests -v
```

## 8. Failure Handling

- Use bounded retries and preserve failed time windows for replay; never advance watermarks past missing or uncommitted data.

## 9. Restrictions

- No credentials in source code, notebooks, or logs.
- No business aggregation inside collectors.
- No direct downstream dependency on provider-specific raw schemas.

## 10. Related Skills

- `kafka-event-streaming`
- `financial-data-quality`
- `data-platform-discovery`
- `data-platform-testing-recovery`

