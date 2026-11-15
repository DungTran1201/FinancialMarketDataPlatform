# Diagram 17 — Domain Microservices Decomposition Topology (`DIAG-C4-017`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-C4-017` |
| **Title** | Domain Microservices Decomposition Topology |
| **Diagram Category** | `docs/diagrams/architecture/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart LR)` |
| **Status** | `IMPLEMENTED` (`docker-compose.yml --profile microservices` + `src/serving/api/services/*.py` + `gateway/service.py`) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/14-data-platform-v01-and-microservices-architecture.md`, `docs/architecture/adr/ADR-007-microservices-and-data-platform-v01.md` |
| **Canonical Model Reference** | `models/architecture/components.yaml`, `models/deployment/deployment.yaml` |
| **Related Artifact IDs** | `ADR-007`, `DEP-006`, `COMP-015`..`COMP-020`, `API-003 (PLANNED)` |

## 1. Purpose

Depicts the decomposition of the Financial Market Data Platform (`ADR-007`) into 7 domain ASGI wrappers (`src/serving/api/services/*.py`, ports `8001`..`8007`) coordinated behind the Unified API Gateway (`svc-api-gateway`, port `8000`) and Nginx `edge-gateway`. Note: `WS /ws/v1/market/stream` (`API-003`) is `[PLANNED]`; real-time Observatory telemetry (`API-055`/`API-056`) is served on `backend-api` via `gateway/observability.py`.

---

## 2. Mermaid Architecture Flowchart (`DIAG-C4-017`)

```mermaid
flowchart LR
    subgraph Clients["External Clients & Operators"]
        UI["Frontend SPA / Client<br/>(https://api.fmdp.local & :3001)"]
        OP["Data Engineer / Operator"]
    end

    subgraph Edge["Gateway & Service Registry (:8000)"]
        GW["svc-api-gateway / backend-api<br/>(Edge Nginx TLS, In-Memory SlidingWindowRateLimiter,<br/>MicroserviceRegistry)"]
    end

    subgraph AppServices["Plane B & C Domain Microservices (src/serving/api/services/)"]
        MKT["svc-market-hot (:8001)<br/>(/api/v1/market; /ws/v1/market/stream PLANNED)"]
        HIST["svc-historical-backfill (:8002)<br/>(/api/v1/historical)"]
        ANA["svc-analytics-quant (:8003)<br/>(/api/v1/analytics)"]
        CAT["svc-catalog-governance (:8004)<br/>(/api/v1/catalog, /api/v1/platform)"]
        IAM["svc-iam-security (:8005)<br/>(/api/v1/auth)"]
        AGT["svc-intelligence-agent (:8006)<br/>(/api/v1/agents, /api/v1/reports)"]
    end

    subgraph DataService["Plane A Data Platform v0.1 Microservice"]
        DP["svc-data-plane-v01 (:8007)<br/>(/api/v1/data-platform/v01/*)"]
    end

    subgraph PolyglotStores["Plane A Polyglot Persistence & Streaming Backbone"]
        RD[("Redis 7 Hot Cache<br/>& Runtime State")]
        CH[("ClickHouse OLAP<br/>ReplacingMergeTree")]
        PG[("PostgreSQL 16 / SQLite WAL<br/>Watermarks, IAM & Reports")]
        LH[("MinIO (:9010) / .local_lakehouse<br/>Bronze, Silver & Gold Marts")]
        KF[["Apache Kafka (1-Node KRaft)<br/>6-Partition Event Backbone"]]
    end

    UI --> GW
    OP --> GW
    GW --> IAM
    GW --> MKT
    GW --> HIST
    GW --> ANA
    GW --> CAT
    GW --> AGT
    GW --> DP

    MKT --> RD
    MKT -. "Fallback (AC-002)" .-> CH
    HIST --> CH
    HIST --> PG
    ANA --> CH
    CAT --> PG
    CAT --> LH
    IAM --> PG
    IAM --> RD
    AGT --> MKT
    AGT --> ANA
    AGT --> PG
    DP --> KF
    DP --> RD
    DP --> CH
    DP --> LH
```

