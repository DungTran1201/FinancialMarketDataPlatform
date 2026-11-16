---
doc_id: "DIAG-C4-CTX-001"
title: "C4 Level 1 — Greenfield System Context Diagram"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "PLANNED"
owner: "Principal Software Architect"
purpose: "Illustrates external actors, Binance & OKX market feeds, and system boundary for the 8 GB single-node Data & Quantitative Intelligence Platform."
scope: "System context across Spot, Perpetual, and Expiry Futures scope."
dependencies:
  - "docs/product/vision-and-scope.md"
  - "docs/architecture/system-architecture-document.md"
references:
  - "docs/diagrams/c4-container.md"
assumptions:
  - "Public read-only market endpoints on Binance and OKX; zero trade-routing connections."
open_issues:
  - "Confirm OKX/Binance regional accessibility during WI-P2-003 API probe."
review_criteria:
  - "Solid lines represent primary active flows; dashed lines optional or recovery paths"
---

# C4 Level 1 — System Context

```mermaid
flowchart TB
    QA["Market Analyst / Trader<br/>(ROLE-QA)"]
    QR["Quant Researcher / ML Eng<br/>(ROLE-QR / ROLE-MLE)"]
    OPS["Platform SRE / Admin<br/>(ROLE-OPS / ROLE-ADM)"]

    SYS["Multi-Asset Data Platform &<br/>Quantitative Intelligence System<br/>(Single-Node 8 GB Architecture)"]

    BIN["Binance Public APIs<br/>(Spot, USDT-M Perp & Delivery<br/>WSS + REST)"]
    OKX["OKX v5 Public APIs<br/>(Spot, Swap, Futures, Opt check<br/>WSS + REST)"]
    E_DISK["Local SSD Storage<br/>(C: Active Working Set <= 5 GB<br/>E: Optional Cold Parquet)"]

    QA -->|HTTPS / WSS: Live Dashboards, OFI, Forecasts| SYS
    QR -->|HTTPS: Datasets, Walk-Forward Evals, Models| SYS
    OPS -->|HTTPS: Config, Backfill, DLQ, 8GB Telemetry| SYS

    BIN -->|WSS Streams & REST Snapshots/Backfill| SYS
    OKX -->|WSS Streams & REST Snapshots/Backfill| SYS
    SYS -->|ZSTD Parquet + SQLite WAL + JetStream FileStore| E_DISK
```

## Legend & Diagram Metadata

- **Solid Arrows (`-->`)**: Primary active external integrations and user-to-system channels.
- **Authoritative Spec**: [vision-and-scope.md](../product/vision-and-scope.md), [system-architecture-document.md](../architecture/system-architecture-document.md).

