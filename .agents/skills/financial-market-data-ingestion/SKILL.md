---
name: financial-market-data-ingestion
description: Exchange REST/WebSocket collectors, Decimal normalization, rate limits, and watermarks.
---

# Skill: Resilient Financial Exchange Ingestion (`SKILL-023`)

## 1. Description

Build and document resilient financial exchange REST (`collector-rest`) and WebSocket (`collector-ws`) ingestion with canonical `EventEnvelopeV1` normalization, exact `Decimal` precision, rate-limit handling, and replayable watermarks.

## 2. Trigger Conditions

- Adding or updating exchange providers, REST pagination, WebSocket streams, gap recovery, provider metadata discovery, or collector behavior (`streaming-data-engineer`, `data-engineer`).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/data-plane/domains/market-data-ingestion/capabilities/exchange-realtime-and-backfill-ingestion/capability.yaml`, `docs/data-plane/shared-contracts/data-contract.yaml`, `docs/data-plane/shared-contracts/asyncapi.yaml`, `src/ingestion/`, `src/shared/contracts/events/market_events.py`, `deploy/postgres/init/01_schema.sql` (`ingestion_watermarks`).

## 4. Preconditions

1. Owning capability `capability.yaml` read; provider, event type, natural key, UTC timestamp source, deterministic ID (`event_id` UUIDv5), target Kafka topic, and partition key (`{provider}:{symbol}`) defined.

## 5. Execution Procedure

1. Isolate provider-specific transport and payload parsing behind ingestion ports (`src/ingestion/domain/ports.py`).
2. Normalize symbols, event types, units, and exact `Decimal` values into `EventEnvelopeV1` (`MarketTradePayloadV1`, `MarketKlinePayloadV1`).
3. Preserve raw source payload and metadata for diagnosis and replay.
4. Implement bounded REST pagination with explicit page boundaries, `HTTP 429` / `418` rate-limit parsing, exponential backoff with jitter, and idempotent resume.
5. Implement WebSocket lifecycle: subscription, heartbeat, reconnect, resubscribe, graceful shutdown, and sequence gap detection.
6. Advance `ingestion_watermarks` only after the designated durable sink has accepted the batch.
7. Route validation failures to `market.dlq.v1` (`DeadLetterEnvelopeV1`) while keeping the collector process healthy.
8. Add unit/contract tests in `tests/`, update ingestion capability docs/contracts if changed, and run `scripts/docs/validate_docs.py` plus `pytest`.

## 6. Output Artifacts

- Provider ingestion adapters (`src/ingestion/`), normalization contract tests (`tests/`), updated Data Plane ingestion capability specs (`docs/data-plane/domains/market-data-ingestion/`), and ingestion runbook notes.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/contract/ tests/resilience/ -v
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
