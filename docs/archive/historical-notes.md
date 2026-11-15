# Historical Architecture Notes & Superseded Designs

| Metadata | Value |
|---|---|
| **Document ID** | `DOC-ARCHIVE-HISTORICAL` |
| **Title** | Historical Architecture Evolution & Superseded Designs Archive |
| **Category** | Historical Archive |
| **Status** | `ARCHIVED` / `SUPERSEDED` |
| **Updated Date** | `2026-11-15` |
| **Authoring Role** | `documentation-architect` |

---

> [!NOTE] Historical Archive Notice
> This document records superseded architectural designs, historical decisions, and evolutionary milestones of the FinancialMarketDataPlatform. For current authoritative architecture, see [docs/overview/system-overview.md](../overview/system-overview.md) and [docs/architecture/00-architecture-overview.md](../architecture/00-architecture-overview.md).

---

## 1. Evolution Milestone 1: The Initial Monolithic Prototype
- **Period**: Early v0.0 phase.
- **Characteristics**: Single Python script ingesting simulated market data into memory. No Kafka streaming backbone, no Lakehouse partitioning, no distributed query engine.
- **Superseded By**: [ADR-001 (Modular Monolith & 3-Plane Separation)](../architecture/adr/ADR-001-overall-architecture.md) and [ADR-002 (Event-Driven Data Platform)](../architecture/adr/ADR-002-event-driven-data-platform.md).

---

## 2. Evolution Milestone 2: Transition from Simulated to Zero-Mock Data Platform (`DATA-001`)
- **Period**: 2026-11-14.
- **Characteristics**: Replaced simulated historical exchange kline collectors (`SimulatedExchangeHistoricalCollector`) with real HTTP REST pagination (`ProductionExchangeHistoricalCollector`), token-bucket rate limiting (`X-MBX-USED-WEIGHT-1M`), SQLite WAL watermark checkpointing, ZSTD Parquet storage, and Apache Iceberg v2 snapshot manifests.
- **Authoritative Record**: [ADR-007 (Zero-Mock E2E Data Platform v0.1)](../architecture/adr/ADR-007-microservices-and-data-platform-v01.md).

---

## 3. Evolution Milestone 3: Modular Restructuring & Domain Alignment (`ARCH-001`)
- **Period**: 2026-11-15.
- **Characteristics**: Transitioned flat package directories (`src/backend/`, `src/consumers/`) into clean architectural boundaries (`src/ingestion/`, `src/streaming/`, `src/lakehouse/`, `src/serving/`, `src/intelligence/`, `src/shared/`).
- **Authoritative Record**: [ADR-008 (Event-Driven Modular Data Platform)](../architecture/adr/ADR-008-event-driven-modular-data-platform.md).

---

## 4. Evolution Milestone 4: Frontend Experience Layer & Microservices Integration (`FEAT-002`)
- **Period**: 2026-11-15.
- **Characteristics**: Replaced prototype static backend HTML pages (`ui.py`) with a dedicated, decoupled TypeScript/Vite Single Page Application served via hardened Nginx, accompanied by Server-Sent Events (SSE) and WebSocket streams.
- **Authoritative Record**: [FEAT-002 Review Record](../../work-items/FEAT-002-frontend-experience-layer/review.md).
