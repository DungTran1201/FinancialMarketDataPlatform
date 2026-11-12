# Diagram 13: Agent Workflow Sequence Diagram

## Architectural Explanation

The **Agent Workflow Sequence Diagram** traces the end-to-end execution of an Agent analysis run across both triggering modes, highlighting how **every quantitative figure is computed deterministically** by the Tool Gateway rather than by LLM arithmetic, and how every step is audited in PostgreSQL.

```mermaid
sequenceDiagram
    autonumber
    actor Trigger as Analyst (API) or Anomaly Detector (Kafka)
    participant API as Agent API / Consumer Gate
    participant PG as PostgreSQL (agent_runs / tool_invocations)
    participant Graph as LangGraph Orchestrator
    participant LLM as LLM Provider Adapter
    participant GW as Controlled Tool Gateway
    participant Quant as Deterministic Quant Engine (ClickHouse / Redis)

    Trigger->>API: Submit Analysis Request / Anomaly Event (BTCUSDT, 24h window)
    API->>PG: Create agent_runs (run_id, status='QUEUED', budget=8000 tokens)
    API-->>Trigger: 202 Accepted (run_id) / Ack Offset

    Graph->>PG: Claim Run -> status='RUNNING'
    Graph->>Graph: Node 1 (Intake): Validate symbol, time bounds & permissions

    loop Bounded Reasoning & Tool Loop (Max 6 Iterations)
        Graph->>LLM: Node 2 (Planner): Provide state + available tool schemas
        LLM-->>Graph: ToolCallRequests: [get_market_snapshot, calculate_volatility, detect_anomalies]
        Graph->>PG: Record token usage & planned tool calls

        par Execute Validated Deterministic Tools via Gateway
            Graph->>GW: Invoke calculate_volatility(symbol='BTCUSDT', interval='1m', window='24h')
            GW->>GW: Validate input schema, enforce max_rows<=1440, set timeout=5s
            GW->>Quant: Query ClickHouse klines & compute exact annualized realized volatility
            Quant-->>GW: Result {volatility_24h: "0.4812", row_count: 1440, as_of: "..."}
            GW->>PG: INSERT agent_tool_invocations (status='SUCCESS', provenance_metadata)
            GW-->>Graph: ToolOutput + ProvenanceCitation
        and
            Graph->>GW: Invoke get_data_freshness(symbol='BTCUSDT')
            GW->>Quant: Check Redis & ClickHouse latest timestamps
            Quant-->>GW: Result {hot_lag_ms: 85, ch_lag_ms: 1200, is_healthy: true}
            GW->>PG: INSERT agent_tool_invocations (status='SUCCESS', provenance_metadata)
            GW-->>Graph: ToolOutput + ProvenanceCitation
        end

        Graph->>Graph: Node 4 (Verifier): Verify tool outputs & data freshness
    end

    Graph->>LLM: Node 5 (Synthesizer): Synthesize StructuredAnalysisReport from deterministic evidence
    LLM-->>Graph: Structured JSON Report (citing exact tool invocation IDs)
    Graph->>GW: Validate report against StructuredAnalysisReport Pydantic schema
    Graph->>PG: UPDATE agent_runs SET status='COMPLETED', structured_report=..., completed_at=NOW()
```

