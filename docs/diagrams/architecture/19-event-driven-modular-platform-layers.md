# Diagram 19 — Event-Driven Modular Data Platform Layers & Dependency Boundaries (`DIAG-C4-019`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-C4-019` |
| **Title** | Event-Driven Modular Data Platform Package & Dependency Boundaries |
| **Diagram Category** | `docs/diagrams/architecture/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart TB)` |
| **Status** | `APPROVED` (`BASELINED`) |
| **Version** | `1.0.0` |
| **Authoritative Document Reference** | `docs/architecture/adr/ADR-008-event-driven-modular-data-platform.md` |
| **Canonical Model Reference** | `models/architecture/architecture.yaml` |
| **Related Artifact IDs** | `ADR-008`, `MODEL-ARCH-001`, `MODEL-ARCH-002`, `TC-006` |

---

## 1. Architectural / Behavioral Explanation

Illustrates the restructured **Event-Driven Modular Data Platform** (`ARCH-001` / `ADR-008`) separating `src/shared/`, `src/ingestion/`, `src/streaming/`, `src/lakehouse/`, `src/serving/`, and `src/intelligence/`. Cross-subsystem AST dependency rules enforced by `tests/architecture/test_clean_architecture_boundaries.py` (`TC-006`) guarantee:
- `src/shared/` holds only genuinely shared contracts, config, domain/quant math, observability, and security primitives with zero dependency on downstream layers.
- `src/ingestion/` depends strictly on `EventPublisherPort` (`src/ingestion/domain/ports.py`) and never imports `src/streaming/`, `src/lakehouse/`, `src/serving/`, or `src/intelligence/`.
- `src/streaming/` owns Kafka broker/topics/consumers and never imports `src/ingestion/`, `src/lakehouse/`, `src/serving/`, or `src/intelligence/`.
- `src/lakehouse/` isolates `bronze`, `silver`, `gold`, `quality`, and `catalog`, coordinated at runtime solely through `src/lakehouse/orchestration/pipeline.py` (composition root).
- `src/serving/api/` preserves the 8-module Clean Architecture Modular Monolith alongside thin ASGI wrappers (`services/`) and Edge Gateway (`gateway/`), with zero dependency on `src/intelligence/`.

---

## 2. Mermaid Diagram View

```mermaid
flowchart TB
    subgraph SharedKernel["src/shared/ (Zero Downstream Dependencies)"]
        SH_CFG["config/settings.py"]
        SH_EVT["contracts/events/market_events.py<br/>& schemas/datasets.py"]
        SH_DOM["domain/primitives.py & quant.py"]
        SH_OBS["observability/metrics.py"]
        SH_SEC["security/primitives.py"]
    end

    subgraph PlaneA["Plane A — Event-Driven Data Platform"]
        subgraph Ingestion["src/ingestion/"]
            ING_DOM["domain/models.py & ports.py<br/>(EventPublisherPort)"]
            ING_APP["application/rate_limiter.py,<br/>ws_service.py, backfill_service.py"]
            ING_PRV["providers/binance/normalizer.py<br/>& rest_client.py"]
            ING_INF["infrastructure/watermark_store.py"]
            ING_ENT["entrypoints/ws_collector.py<br/>& rest_backfill.py"]
        end

        subgraph Streaming["src/streaming/"]
            STR_CON["contracts/topics.py<br/>(6 Canonical Topics)"]
            STR_INF["infrastructure/kafka_broker.py"]
            STR_CSM["consumers/anomaly_detector.py,<br/>hot_redis.py, analytics_ch.py"]
        end

        subgraph Lakehouse["src/lakehouse/"]
            LH_BRZ["bronze/archiver.py & consumer.py"]
            LH_SLV["silver/merge_engine.py"]
            LH_GLD["gold/mart_engine.py & dbt/"]
            LH_DQ["quality/gates.py"]
            LH_CAT["catalog/lineage.py"]
            LH_ORC["orchestration/pipeline.py<br/>(Composition Root)"]
        end
    end

    subgraph PlaneB["Plane B — Serving & Control Plane (src/serving/)"]
        SRV_GW["api/gateway/ (registry, service, ui)"]
        SRV_MOD["api/modules/ (8 Clean Architecture Domains)"]
        SRV_SVC["api/services/ (8 ASGI Wrappers)"]
        SRV_APP["api/main.py & infrastructure/runtime.py"]
    end

    subgraph PlaneC["Plane C — Intelligence Plane (src/intelligence/)"]
        INT_ORC["orchestrator/graph.py & main.py"]
        INT_WF["workflows/investigation.py"]
        INT_TOOL["tools/contracts.py & gateway.py"]
        INT_REP["reporting/validator.py"]
    end

    Ingestion --> SharedKernel
    Streaming --> SharedKernel
    LH_BRZ --> SharedKernel
    LH_SLV --> SharedKernel
    LH_GLD --> SharedKernel
    LH_DQ --> SharedKernel
    LH_CAT --> SharedKernel
    SRV_MOD --> SharedKernel
    INT_TOOL --> SharedKernel

    LH_ORC -->|"Wires"| Ingestion
    LH_ORC -->|"Wires"| Streaming
    LH_ORC -->|"Wires"| Lakehouse

    SRV_APP -->|"Composes (No Plane C Direct Import)"| PlaneA
    INT_TOOL -.->|"Read-Only Adapters"| SRV_MOD
```

