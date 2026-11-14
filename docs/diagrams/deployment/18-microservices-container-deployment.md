# Diagram 18 — Microservices Container Deployment & Network Isolation (`DIAG-DEP-018`)

## 1. Purpose

Illustrates the Docker Compose `--profile microservices` (`DEP-006`) container deployment topology across the three segmented internal networks (`frontend_net`, `app_control_net`, `data_plane_net`).

---

## 2. Mermaid Deployment Flowchart (`DIAG-DEP-018`)

```mermaid
flowchart TB
    subgraph FrontendNet["frontend_net (TLS Ingress & Gateway)"]
        GW["svc-api-gateway / backend-api<br/>(Port 8000)"]
    end

    subgraph AppControlNet["app_control_net (Domain Microservices & Control Plane)"]
        S1["svc-market-hot (:8001)"]
        S2["svc-historical-backfill (:8002)"]
        S3["svc-analytics-quant (:8003)"]
        S4["svc-catalog-governance (:8004)"]
        S5["svc-iam-security (:8005)"]
        S6["svc-intelligence-agent (:8006)"]
        S7["svc-data-plane-v01 (:8007)"]
        PG[("postgres:16-alpine (:5432)")]
        PROM["prometheus (:9090)"]
    end

    subgraph DataPlaneNet["data_plane_net (Streaming, Hot Cache, OLAP & Lakehouse)"]
        KFK[["kafka KRaft (:9092)"]]
        RDS[("redis:7.2-alpine (:6379)")]
        CLK[("clickhouse-server (:8123)")]
        MNO[("minio Iceberg S3 (:9000)")]
    end

    GW --> S1
    GW --> S2
    GW --> S3
    GW --> S4
    GW --> S5
    GW --> S6
    GW --> S7

    S1 --> RDS
    S1 --> CLK
    S2 --> CLK
    S2 --> PG
    S3 --> CLK
    S4 --> PG
    S4 --> MNO
    S5 --> PG
    S5 --> RDS
    S6 --> PG
    S7 --> KFK
    S7 --> RDS
    S7 --> CLK
    S7 --> MNO
    PROM --> S7
    PROM --> GW
```

