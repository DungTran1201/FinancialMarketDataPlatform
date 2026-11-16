---
doc_id: DIAG-DP-ING-TM-001
title: "Diagram: Exchange Ingestion Threat Model & Trust Boundaries"
doc_type: diagram
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/data-plane/domains/market-data-ingestion/capabilities/exchange-realtime-and-backfill-ingestion/security/threat-model.md"
related_docs:
  - CAP-DP-ING-TM-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Derived trust boundary diagram explicitly marking SEC-AUDIT-003 HTTP trigger gap."
---

# Diagram: Exchange Ingestion Threat Model & Trust Boundaries

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-DP-ING-TM-001` |
| **Title & Purpose** | Shows trust boundaries across external Binance feeds, HTTP API triggers, normalizer validation, and SQLite/Kafka stores |
| **Owner Role & Scope** | `security-architect / CAP-DP-ING-001` |
| **Authoritative Source** | [threat-model.md](threat-model.md) (`CAP-DP-ING-TM-001`) |
| **Notation** | `Mermaid flowchart TB` (`Trust Boundary DFD`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
flowchart TB
    ext_feed["Untrusted External Exchange JSON (Binance)"]
    ext_caller["HTTP Client / Potential Attacker"]

    subgraph tb_api["Trust Boundary 1: Serving Trigger Edge"]
        ep_trigger["POST /market/ingest & /historical/backfill-jobs [GAP: SEC-AUDIT-003 No Auth]"]
    end

    subgraph tb_core["Trust Boundary 2: Ingestion Validation Core"]
        norm["BinancePayloadNormalizer [SEC-ING-001 Strict Decimal/Schema]"]
        limiter["TokenBucketRateLimiter (960 weight/min cap)"]
        wm[("SQLite Watermark Store")]
        dlq[("market.dlq.v1")]
    end

    ext_caller -->|"THR-ING-002: Abusive Trigger"| ep_trigger
    ep_trigger -->|"Triggers"| limiter
    ext_feed -->|"THR-ING-001: Poison / Corrupt JSON"| norm
    norm -.->|"Quarantine Invalid"| dlq
    limiter -->|"Bounded REST Pull"| norm
    norm -->|"State Write"| wm
```

## 3. Legend `[REQUIRED]`

- **Subgraphs**: Explicit privilege/validation trust boundaries.
- **`[GAP: ...]`**: Confirmed missing authentication control (`SEC-AUDIT-003`); never treated as mitigated.
