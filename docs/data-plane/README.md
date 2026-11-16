---
doc_id: DP-ROOT-001
title: "Data Plane — Realtime Financial Market Data Platform"
doc_type: index
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
    - "docs/data-plane/README.md"
related_docs:
  - DOC-ROOT-001
  - OVR-ARCH-3P-001
  - DP-ARCH-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: data-architect
    summary: "Initialized Phase 2 Data Plane portal registering architecture, shared contracts, 3 domains, and 4 capabilities."
---

# Data Plane — Realtime Financial Market Data Platform

The Data Plane owns external exchange market data acquisition (`src/ingestion/`), canonical event contracts (`src/shared/contracts/`), Kafka streaming & DLQ isolation (`src/streaming/`), monotonic hot cache & OLAP analytical sinks, statistical anomaly emission, medallion Bronze/Silver/Gold lakehouse datasets (`src/lakehouse/`), and data quality/lineage governance.

## 1. Plane Architecture & Operations

- [architecture/README.md](architecture/README.md): Architecture viewpoints (`C4 L2 Container`, `DFD`, Storage tiers, Scalability/Resilience, Observability, Security, Decisions)
- [shared-contracts/README.md](shared-contracts/README.md): Canonical [asyncapi.yaml](shared-contracts/asyncapi.yaml) (`AsyncAPI 3.1.0`) & [data-contract.yaml](shared-contracts/data-contract.yaml)
- [operations/runbook.md](operations/runbook.md), [operations/incident-and-recovery.md](operations/incident-and-recovery.md), [operations/observability-and-slo.md](operations/observability-and-slo.md), [operations/test-plan.md](operations/test-plan.md)

## 2. Domains & Capabilities Registry

| Domain | Capabilities | Risk Tier | Implementation Status |
|---|---|---|---|
| [market-data-ingestion](domains/market-data-ingestion/README.md) | `CAP-DP-ING-001`: [exchange-realtime-and-backfill-ingestion](domains/market-data-ingestion/capabilities/exchange-realtime-and-backfill-ingestion/README.md) | `HIGH_CRITICAL` | `PARTIALLY_IMPLEMENTED` |
| [event-streaming](domains/event-streaming/README.md) | `CAP-DP-STR-001`: [kafka-event-bus-and-dlq](domains/event-streaming/capabilities/kafka-event-bus-and-dlq/README.md)<br>`CAP-DP-STR-002`: [realtime-hot-state-and-olap-projection](domains/event-streaming/capabilities/realtime-hot-state-and-olap-projection/README.md) | `HIGH_CRITICAL` | `SIMULATED` |
| [lakehouse-analytics](domains/lakehouse-analytics/README.md) | `CAP-DP-LAK-001`: [medallion-lakehouse-and-quality-gates](domains/lakehouse-analytics/capabilities/medallion-lakehouse-and-quality-gates/README.md) | `MEDIUM` | `PARTIALLY_IMPLEMENTED` |
