---
doc_id: ADR-DP-001
title: "ADR-DP-001: At-Least-Once Event Delivery with Deterministic UUIDv5 & Natural-Key Sinks"
doc_type: adr
plane: data-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/shared/contracts/events/market_events.py"
    - "src/streaming/consumers/hot_redis.py"
    - "src/lakehouse/silver/merge_engine.py"
related_docs:
  - DP-ARCH-001
  - DP-ARCH-RES-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Formalized MADR decision avoiding false distributed exactly-once claims in favor of idempotent sinks + manual commits."
---

# ADR-DP-001: At-Least-Once Event Delivery with Deterministic UUIDv5 & Natural-Key Sinks

## 1. Context and Problem Statement `[REQUIRED]`

Replay after WebSocket gaps, REST backfills, or consumer restarts inevitably delivers duplicate or out-of-order trade/kline events. Cross-system distributed 2PC transactions across Kafka, Redis, ClickHouse, and Parquet/Iceberg are unavailable or brittle.

## 2. Considered Options `[REQUIRED]`

1. **Claim Distributed Exactly-Once End-to-End**: Attempt distributed transactions across Kafka + all heterogeneous stores.
2. **At-Least-Once Delivery + Deterministic Identity + Idempotent Sinks**: Compute deterministic UUIDv5 `event_id`s, partition by `{provider}:{symbol}` to preserve symbol ordering, commit offsets manually **after** sink writes succeed, and enforce sink-level idempotency (Redis monotonic Lua timestamp check, ClickHouse `ReplacingMergeTree`, Silver natural-key merge).

## 3. Decision Outcome `[REQUIRED]`

Adopt **Option 2**. Delivery is explicitly documented as **at-least-once with idempotent sinks** (effectively-once per natural key on replay), never distributed exactly-once.

## 4. Consequences `[REQUIRED]`

- **Positive**: Replay tests (`test_medallion_quality_gates.py`, `test_three_planes_framework.py`) prove zero duplicate rows on kline/trade replay and deterministic monotonic drop of stale prices.
- **Negative / Operational**: Live `confluent_kafka` consumer loops and live `ClickHouse`/`Redis` write paths remain `NOT_IMPLEMENTED` / `SIMULATED` and must preserve commit-after-write semantics when wired.
