---
doc_id: "DIAG-SEC-TM-001"
title: "Trust Boundaries & Security Control Diagram"
version: "1.0.0"
status: "IN_REVIEW"
implementation_status: "NOT_IMPLEMENTED"
owner: "Security Engineer"
purpose: "Depicts trust boundaries TB-1..TB-4, attack vectors THR-01..THR-07, and mandatory mitigations."
scope: "All network, IPC, and disk persistence boundaries."
dependencies:
  - "docs/architecture/threat-model.md"
references:
  - "docs/product/acceptance-criteria.md"
assumptions:
  - "TLS 443 used exclusively for outbound public market feeds; local API binds loopback or TLS proxy."
open_issues: []
review_criteria:
  - "Every threat THR-01..THR-07 visibly anchored to a trust boundary"
---

# Security Threat Model Diagram

```mermaid
flowchart LR
    EXT_EX["Untrusted Public Exchanges<br/>(Binance / OKX Feeds)"] -->|TB-1: THR-04 Poison JSON / Gaps| NORM_GUARD["Schema/Decimal Gate<br/>+ Size Limits + DLQ Quarantine"]

    USER["Browser / API Caller"] -->|TB-3: THR-01 Auth Bypass / THR-02 XFF Spoof / THR-06 WS Flood| EDGE_GUARD["FastAPI JWT/API-Key Auth + RBAC<br/>+ Trusted Proxy Only + Conflated WS"]

    EDGE_GUARD -->|Parameter Validated Only| DUCK_GUARD["TB-4: THR-03 DuckDB Path/SQL Guard<br/>(No Raw SQL; Bounded Base Path)"]
    DUCK_GUARD --> PQ[("Parquet & Model Registry<br/>THR-07 Safe Serialization (No untrusted pickle)")]

    EDGE_GUARD -->|Authenticated Events| NATS_BUS["TB-2: THR-05 Loopback NATS<br/>127.0.0.1:4222 + Auth Token"]
    NORM_GUARD --> NATS_BUS
```

## Legend & Diagram Metadata

- **Trust Boundaries (`TB-1..TB-4`)**: Explicit boundary points enforcing schema sanitization, RBAC, parameterized DuckDB guards, and safe artifact loading.
- **Authoritative Spec**: [threat-model.md](../architecture/threat-model.md).
