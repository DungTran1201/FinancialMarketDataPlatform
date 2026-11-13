# Data Rule — Ingestion Reliability, Watermarks and Backfill (`DATA-RULE-004`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-004` |
| **Rule Slug** | `ingestion-reliability` |
| **Trigger Scope** | REST pagination, WebSocket collectors, source adapters, gap recovery, backfill, and ingestion watermark updates |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Enforces resilient exchange ingestion across WebSocket (`collector-ws`) and REST (`collector-rest`) collectors, including rate-limit backoff, reconnect gap detection, and durable watermark advancement.

## 2. Mandatory Directives

1. **Resilient Transport**: Make reconnect, heartbeat/timeout, rate-limit handling (`HTTP 429` / `418`), bounded exponential backoff with jitter, and graceful shutdown explicit.
2. **Durable Watermark Advancement**: Advance `ingestion_watermarks` in PostgreSQL only after the corresponding data batch is durably accepted by the designated sink.
3. **Replay & Natural Keys**: Define inclusive/exclusive page boundaries, overlap windows, late events, replay windows, and deterministic UUIDv5 natural keys.
4. **Quarantine & Telemetry**: Route malformed payloads to `market.dlq.v1` with raw payload preservation and track source freshness/gaps at bounded metric cardinality.

## 3. Prohibited Actions

- Do not advance ingestion watermarks before durable sink writes complete.
- Do not use unbounded hot retry loops or silently skip rate-limited pages.
- Do not conflate a WebSocket reconnect with completed historical gap recovery.

## 4. Verification Mechanism

- Collector unit/integration tests covering disconnect/reconnect, rate limits, partial pagination, duplicate replay, and watermark recovery, plus `tools/validators/run_all.py`.

