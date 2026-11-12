# Diagram 14: Agent Tool Access & Security Guardrail Diagram

## Architectural Explanation

The **Agent Tool Access Diagram** illustrates the security boundary between the non-deterministic LLM reasoning engine and the platform's data stores. The LLM has **zero network or credential access** to Redis, ClickHouse, PostgreSQL, or MinIO. Instead, every tool request passes through five mandatory enforcement gates inside the **Controlled Tool Gateway**:
1. **Tool Whitelist & RBAC Check**: Confirms the tool is in the 10 approved read-only tools and permitted for the caller's role.
2. **Pydantic Strict Input Validation**: Rejects any SQL fragments, invalid symbols, or time windows exceeding maximum lookback bounds.
3. **Resource & Timeout Sandbox**: Wraps execution in `asyncio.wait_for(timeout=5.0)` and binds ClickHouse `max_execution_time=5`, `max_rows_to_read=500000`, `readonly=1`.
4. **Deterministic Python/SQL Execution**: Computes returns, volatility, correlations, and Z-scores using exact decimal/NumPy routines over ClickHouse/Redis read-only adapters.
5. **Provenance & Audit Stamp**: Attaches `invocation_id`, `source_store`, `time_range`, `row_count`, and `sha256_evidence_hash` before returning the result to the LangGraph state.

```mermaid
flowchart LR
    subgraph UntrustedReasoning["Probabilistic LLM Boundary"]
        LLMNode["LangGraph Planner Node<br/>(Emits Structured Tool Call JSON)"]
    end

    subgraph ToolGatewayBoundary["Controlled Tool Gateway (Security & Determinism Firewall)"]
        direction TB
        G1["Gate 1: Tool Whitelist & RBAC Policy<br/>(Only 10 Approved Read-Only Tools)"]
        G2["Gate 2: Strict Schema & Bound Validator<br/>(Pydantic v2, Max Lookback Window, Max Limit)"]
        G3["Gate 3: Execution Timeout & Query Cost Guard<br/>(5s Timeout, ClickHouse readonly=1, max_rows Cap)"]
        G4["Gate 4: Deterministic Compute Engine<br/>(Exact Returns, Volatility, Correlation, Anomaly Z-Score)"]
        G5["Gate 5: Provenance Tagger & Audit Logger<br/>(Attach Source, Window, RowCount, Hash)"]

        G1 --> G2 --> G3 --> G4 --> G5
    end

    subgraph ApprovedTools["Catalog of 10 Deterministic Tools"]
        direction TB
        CatMarket["Market Tools:<br/>1. get_latest_price<br/>2. get_market_snapshot<br/>3. get_historical_candles<br/>4. get_market_statistics"]
        CatQuant["Quantitative Tools:<br/>5. calculate_returns<br/>6. calculate_volatility<br/>7. calculate_correlation"]
        CatDiag["Diagnostic & Output Tools:<br/>8. detect_anomalies<br/>9. get_data_freshness<br/>10. generate_analysis_report"]
    end

    subgraph ReadOnlyStores["Least-Privilege Data Stores"]
        RedisRO[("Redis 7<br/>(Read-Only Hot Keys)")]
        CHRO[("ClickHouse<br/>(User: agent_ro, readonly=1)")]
        PGAudit[("PostgreSQL<br/>(Write Audit Trail Only)")]
    end

    subgraph Blocked["Strictly Prohibited Actions"]
        NoSQL["X Arbitrary Raw SQL Execution"]
        NoWrite["X Mutating Market or Lakehouse Data"]
        NoTrade["X Executing Exchange Orders"]
    end

    LLMNode -->|"JSON Tool Call"| G1
    LLMNode -.->|"Blocked by Design"| Blocked

    G4 --> CatMarket & CatQuant & CatDiag
    CatMarket --> RedisRO & CHRO
    CatQuant --> CHRO
    CatDiag --> RedisRO & CHRO
    G5 -->|"Log Invocation"| PGAudit
    G5 -->|"Verified Evidence + Provenance"| LLMNode
```

