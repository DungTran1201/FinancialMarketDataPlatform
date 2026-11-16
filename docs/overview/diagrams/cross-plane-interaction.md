---
doc_id: OVR-DIAG-XPL-001
title: "Diagram: Cross-Plane Runtime Interaction Sequence"
doc_type: diagram
plane: platform
scope_level: platform
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: system-architect
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/overview/cross-plane-interactions.md"
related_docs:
  - OVR-ARCH-XPL-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: system-architect
    summary: "Derived chronological cross-plane interaction sequence verifying hot-cache fallback and synchronous Agent investigation execution."
---

# Diagram: Cross-Plane Runtime Interaction Sequence

## 1. Diagram Metadata `[REQUIRED]`

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-OVR-XPL-001` |
| **Title & Purpose** | Chronological sequence across Application, Data, and Intelligence Planes for quote fallback and Agent runs |
| **Owner Role & Scope** | `system-architect / platform` |
| **Authoritative Source** | [cross-plane-interactions.md](../cross-plane-interactions.md) (`OVR-ARCH-XPL-001`) |
| **Notation** | `Mermaid sequenceDiagram` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram `[REQUIRED]`

```mermaid
sequenceDiagram
    autonumber
    actor User as "Browser / API Caller"
    participant App as "Application Plane (FastAPI Router + Runtime)"
    participant Hot as "Data Plane (HotStateProjector)"
    participant CH as "Data Plane (ClickHouseBatchSink)"
    participant Graph as "Intelligence Plane (MarketIntelligenceGraph)"
    participant GW as "ControlledToolGateway"

    User->>+App: "GET /api/v1/market/prices/{symbol} (No Auth Guard AS-IS)"
    App->>+Hot: "get_hot_price(provider, symbol)"
    alt "Hot Cache Hit"
        Hot-->>-App: "HotPriceRecord (is_stale=false)"
        App-->>User: "200 OK (meta.source=redis_hot_cache)"
    else "Hot Cache Miss"
        App->>+CH: "Fallback query latest kline/price"
        CH-->>-App: "OLAP price or None (is_stale=true)"
        App-->>-User: "200 OK (clickhouse_fallback) or 404 ERR_SYMBOL_NOT_FOUND"
    end

    User->>+App: "POST /api/v1/agents/runs (Idempotency-Key)"
    Note over App,Graph: "AS-IS executes synchronously via await despite 202 status code"
    App->>+Graph: "run_investigation(AgentWorkflowState)"
    Graph->>+GW: "execute_tool(7 planned read tools, rbac_perms)"
    GW->>Hot: "get_latest_price / snapshot / freshness"
    GW->>CH: "get_historical_candles / log returns / volatility / anomaly"
    GW-->>-Graph: "ToolExecutionEnvelope[] (with UUID invocation_id)"
    Graph->>GW: "execute_tool('generate_analysis_report')"
    GW->>App: "Write StructuredAnalysisReport to runtime.reports"
    Graph-->>-App: "AgentWorkflowState (COMPLETED)"
    App-->>-User: "202 Accepted (run_id, status=COMPLETED)"
```

## 3. Legend `[REQUIRED]`

- **Solid Arrow (`->>`)**: Synchronous HTTP or in-process Python `await` call.
- **Dashed Arrow (`-->>`)**: Return value or HTTP response.
- **`alt` / `else`**: Hot-cache hit vs. ClickHouse OLAP fallback branch.
