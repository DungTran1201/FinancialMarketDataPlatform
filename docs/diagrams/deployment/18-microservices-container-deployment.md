# Diagram 18 — Microservices Container Deployment & Network Isolation (`DIAG-DEP-018`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-DEP-018` |
| **Title** | Microservices Container Deployment & Network Isolation |
| **Diagram Category** | `docs/diagrams/deployment/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart TB)` |
| **Status** | `IMPLEMENTED` |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/12-deployment-architecture.md`, `docs/architecture/14-data-platform-v01-and-microservices-architecture.md` |
| **Canonical Model Reference** | `models/deployment/deployment.yaml` |
| **Related Artifact IDs** | `DEP-006`, `ADR-007` |

## 1. Purpose

Illustrates the Docker Compose `--profile microservices` (`DEP-006`, paired with `core`, `lakehouse`, and `observability` profiles) container deployment topology across the three segmented networks (`frontend_net`, `app_control_net`, `data_plane_net`).

---

## 2. Mermaid Deployment Flowchart (`DIAG-DEP-018`)

```mermaid
flowchart TB
    subgraph FrontendNet["frontend_net (Edge TLS, Frontend SPA & Gateway)"]
        Edge["edge-gateway (:80/:443)"]
        UI["frontend (:3001->:3000)"]
        GW["backend-api / svc-api-gateway<br/>(:8000; attached to all 3 nets)"]
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
        PROM["prometheus (:9090)<br/>[app_control_net + data_plane_net]"]
    end

    subgraph DataPlaneNet["data_plane_net (Streaming, Hot Cache, OLAP & Lakehouse)"]
        KFK[["kafka 1-Node KRaft (:9092)"]]
        RDS[("redis:7.2-alpine (:6379)")]
        CLK[("clickhouse-server (:8123/:9000)")]
        MNO[("minio Iceberg S3 (:9010->:9000, :9001)")]
    end

    Edge --> UI & GW
    GW --> S1 & S2 & S3 & S4 & S5 & S6 & S7

    S1 --> RDS & CLK
    S2 --> CLK & PG
    S3 --> CLK
    S4 --> PG & MNO
    S5 --> PG & RDS
    S6 --> PG
    S7 --> KFK & RDS & CLK & MNO
    PROM -->|"Scrape :8007 metrics"| S7
    PROM -->|"Scrape :8000 /metrics"| GW
```

