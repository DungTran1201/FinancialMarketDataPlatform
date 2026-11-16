---
doc_id: DP-CTR-ROOT-001
title: "Data Plane Shared Event & Dataset Contracts Index"
doc_type: index
plane: data-plane
scope_level: plane
status: IN_REVIEW
implementation_status: IMPLEMENTED
version: "2.0.0"
owner_role: data-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/shared/contracts/events/market_events.py"
    - "src/shared/contracts/schemas/datasets.py"
    - "src/streaming/contracts/topics.py"
related_docs:
  - DP-ROOT-001
  - OVR-ARCH-XPL-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Established single authoritative Data Plane contract hub referenced by all internal and cross-plane consumers."
---

# Data Plane Shared Contracts

Consumers across the Application Plane and Intelligence Plane MUST reference these canonical contracts rather than duplicating schemas locally.

- [asyncapi.yaml](asyncapi.yaml): AsyncAPI `3.1.0` contract covering all 6 canonical Kafka topics (`market.raw.trades.v1`, `market.raw.klines.v1`, `market.raw.tickers.v1`, `market.raw.orderbook.v1`, `market.anomalies.v1`, `market.dlq.v1`) and 4 consumer groups.
- [data-contract.yaml](data-contract.yaml): Canonical `EventEnvelopeV1`, `DeadLetterEnvelopeV1`, and 6 Silver/Gold dataset contracts (`CANONICAL_DATASET_CONTRACTS`).
