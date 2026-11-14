# Diagram 17 — Domain Microservices Decomposition Topology (`DIAG-C4-017`)

## 1. Purpose

Depicts the decomposition of the Financial Market Data Platform on branch `arch/microservices` (`ADR-007`) into 8 independently deployable domain microservices behind the Unified HTTPS API Gateway (`svc-api-gateway`).

---

## 2. Mermaid Architecture Flowchart (`DIAG-C4-017`)

```mermaid
flowchart LR
    subgraph Clients["External Clients & Operators"]
        UI["Web / Trader Client<br/>(https://api.fmdp.local)"]
        OP["Data Engineer / Operator"]
    end

    subgraph Edge["Edge Gateway & Service Registry (:8000)"]
        GW["svc-api-gateway<br/>(HTTPS, WAF, Sliding-Window Rate Limiter,<br/>MicroserviceRegistry)"]
    end

    subgraph AppServices["Plane B & C Domain Microservices"]
        MKT["svc-market-hot (:8001)<br/>(/api/v1/market, /ws/v1/market)"]
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
        RD[("Redis 7 Hot Cache<br/>& Rate Limiter")]
        CH[("ClickHouse OLAP<br/>ReplacingMergeTree")]
        PG[("PostgreSQL 16 / SQLite<br/>Watermarks, IAM & Reports")]
        LH[("MinIO / Iceberg v2<br/>Bronze, Silver & Gold Marts")]
        KF[["Apache Kafka (KRaft)<br/>6-Partition Event Backbone"]]
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

