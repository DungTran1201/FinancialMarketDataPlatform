# Diagram 14: Agent Tool Access & Security Guardrail Diagram (`DIAG-SEC-014`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-SEC-014` (legacy `DOCS-002` alias: `DIAG-COMP-014`) |
| **Title** | Agent Tool Access & Security Guardrail Architecture |
| **Diagram Category** | `docs/diagrams/agent/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart LR)` |
| **Status** | `IMPLEMENTED` / `PARTIALLY_IMPLEMENTED` (10-tool `ControlledToolGateway` & bounds active in `src/intelligence/tools/`; ClickHouse dedicated `fmdp_agent_ro` SQL user `[PLANNED]`) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/06-agentic-intelligence-architecture.md`, `docs/architecture/10-security-and-governance.md` |
| **Canonical Model Reference** | `models/architecture/components.yaml`, `models/security/threat-model.yaml` |
| **Related Artifact IDs** | `THR-005`, `CTRL-005`, `COMP-005`, `TC-005` |

## Architectural Explanation

The **Agent Tool Access Diagram** illustrates the security boundary between the reasoning layer and platform data stores (`src/intelligence/tools/contracts.py` & `gateway.py`):
1. **Tool Whitelist & Permission Mapping**: Confirms the tool is in `ApprovedAgentTool` (the **10** approved read-only tools) and checks `required_permission` (`market:read`, `historical:read`, `analytics:read`).
2. **Strict Bound Validator**: Rejects SQL fragments, invalid symbols, or row/period windows exceeding `max_rows_or_periods` (`1`, `168`, `500`, `720`, or `2160` per tool policy).
3. **Per-Tool Timeout Guard**: Enforces `timeout_seconds` per `APPROVED_TOOL_POLICIES` (`1.5s` to `8.0s`).
4. **Deterministic Python/OLAP Execution**: Computes returns, volatility, correlations, and Z-scores using exact deterministic math over read-only adapters (note: dedicated ClickHouse `fmdp_agent_ro` database user in Compose init is `[PLANNED]`).
5. **Provenance & Audit Stamp**: Attaches `invocation_id`, `source_store`, `symbol`, and `row_count` in every `ToolExecutionEnvelope`.

```mermaid
flowchart LR
    subgraph UntrustedReasoning["Probabilistic LLM Boundary"]
        LLMNode["MarketIntelligenceGraph Planner<br/>(Emits Structured Tool Call Requests)"]
    end

    subgraph ToolGatewayBoundary["ControlledToolGateway (src/intelligence/tools/)"]
        direction TB
        G1["Gate 1: ApprovedAgentTool Whitelist<br/>(Exactly 10 Approved Tools)"]
        G2["Gate 2: Strict Parameter & Row/Period Bound<br/>(1..2160 periods by Tool Policy)"]
        G3["Gate 3: Per-Tool Execution Timeout<br/>(1.5s..8.0s by ToolGovernancePolicy)"]
        G4["Gate 4: Deterministic Compute Engine<br/>(Exact Returns, Volatility, Correlation, Z-Score)"]
        G5["Gate 5: Provenance Tagger & Evidence Trail<br/>(invocation_id, source_store, row_count)"]

        G1 --> G2 --> G3 --> G4 --> G5
    end

    subgraph ApprovedTools["Catalog of 10 Deterministic Tools (contracts.py)"]
        direction TB
        CatMarket["Market Tools:<br/>1. get_latest_price<br/>2. get_market_snapshot<br/>3. get_historical_candles<br/>4. get_market_statistics"]
        CatQuant["Quantitative Tools:<br/>5. calculate_returns<br/>6. calculate_volatility<br/>7. calculate_correlation"]
        CatDiag["Diagnostic & Output Tools:<br/>8. detect_anomalies<br/>9. get_data_freshness<br/>10. generate_analysis_report"]
    end

    subgraph ReadOnlyStores["Data Stores (Read-Only Tool Adapters)"]
        RedisRO[("Redis 7 / HotStateProjector<br/>(Read-Only Hot Keys)")]
        CHRO[("ClickHouse / OLAP Adapter<br/>(Dedicated fmdp_agent_ro readonly=1 PLANNED)")]
        PGAudit[("Runtime / PostgreSQL [PLANNED Worker PG]<br/>(Audit Trail Only)")]
    end

    subgraph Blocked["Strictly Prohibited Actions"]
        NoSQL["X Arbitrary Raw SQL Execution"]
        NoWrite["X Mutating Market or Lakehouse Data"]
        NoTrade["X Executing Exchange Orders"]
    end

    LLMNode -->|"Tool Call JSON"| G1
    LLMNode -.->|"Blocked by Design"| Blocked

    G4 --> CatMarket & CatQuant & CatDiag
    CatMarket --> RedisRO & CHRO
    CatQuant --> CHRO
    CatDiag --> RedisRO & CHRO
    G5 -->|"Record Evidence"| PGAudit
    G5 -->|"Verified Evidence + Provenance"| LLMNode
```

