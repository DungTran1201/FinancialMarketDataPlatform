# Diagram 12: Agentic Intelligence Architecture

## Architectural Explanation

The **Agentic Intelligence Architecture** illustrates how the **Intelligence Plane** operates as an isolated service (`agent-worker` + `agent_api` module) powered by **LangGraph**:
- **Dual Trigger Entrypoints**:
  1. **On-Demand Analysis**: Triggered via `POST /api/v1/agents/runs` by an authenticated analyst.
  2. **Event-Triggered Investigation**: Triggered when the deterministic `StatisticalAnomalyDetector` publishes a breach event to `market.anomalies.v1` and passes the deduplication cooldown filter (e.g., 15-minute window per symbol/detector).
- **Stateful LangGraph Orchestrator (`MarketIntelligenceGraph`)**:
  - Executes explicit state nodes (`Intake & Scope Validation` $\rightarrow$ `Tool Planning` $\rightarrow$ `Controlled Tool Gateway Execution` $\rightarrow$ `Evidence Verification` $\rightarrow$ `Structured Report Synthesis`).
  - Persists state checkpoints, tool invocation trails, token usage, and final reports to **PostgreSQL**.
- **Strict Isolation**: The Intelligence Plane accesses market data exclusively in **read-only** mode through the **Deterministic Tool Gateway** and can fail completely without affecting the Data Plane.

```mermaid
flowchart TB
    subgraph Triggers["1. Agent Triggering Modes"]
        UserTrigger["On-Demand Request<br/>POST /api/v1/agents/runs"]
        AnomalyStream["Event-Triggered Anomaly<br/>Kafka: market.anomalies.v1"]
        CooldownFilter["Deterministic Deduplication & Cooldown Gate<br/>(Redis Key: agent:cooldown:{symbol}:{detector})"]
    end

    subgraph AgentService["2. Intelligence Plane: LangGraph Agent Service"]
        subgraph LangGraphWorkflow["LangGraph Stateful Workflow (MarketIntelligenceGraph)"]
            N1["Node 1: Intake & Guardrail Validator<br/>(Verify Scope, Time Window, Token Budget)"]
            N2["Node 2: Investigation Planner<br/>(Select Deterministic Tools)"]
            N3["Node 3: Tool Gateway Executor<br/>(Run Quant & Data Tools in Parallel/Sequence)"]
            N4["Node 4: Evidence Verifier<br/>(Check Provenance, Completeness & Bounds)"]
            N5["Node 5: Structured Report Synthesizer<br/>(Generate JSON Report with Citations)"]

            N1 --> N2 --> N3 --> N4
            N4 -->|"Need Additional Evidence (Max 6 Steps)"| N2
            N4 -->|"Sufficient Deterministic Evidence"| N5
        end

        LLMAdapter["LLM Provider Adapter<br/>(Timeout, Retry, Token Meter, Circuit Breaker)"]
        ToolGW["Controlled Tool Gateway<br/>(RBAC, Schema Validation, Query Cap, Provenance Tagger)"]
    end

    subgraph DeterministicTools["3. Deterministic Analytical & Data Tools (Python / SQL)"]
        TPrice["get_latest_price / get_market_snapshot"]
        THist["get_historical_candles / get_market_statistics"]
        TQuant["calculate_returns / calculate_volatility / calculate_correlation"]
        TAnom["detect_anomalies / get_data_freshness"]
        TRep["generate_analysis_report"]
    end

    subgraph DataAndState["4. Persistence & Read-Only Data Sources"]
        PGState[("PostgreSQL (agent_rw)<br/>agent_runs & agent_tool_invocations")]
        RedisRO[("Redis (Read-Only)<br/>Hot Market State")]
        CHRO[("ClickHouse (agent_ro)<br/>Bounded Analytical Queries")]
        LLMCloud["External LLM API"]
    end

    UserTrigger -->|"Enqueue Run"| PGState
    AnomalyStream --> CooldownFilter
    CooldownFilter -->|"Passed Cooldown"| N1
    PGState -->|"Dequeue Run"| N1

    N2 & N5 <-->|"Structured Prompt / Schema"| LLMAdapter
    LLMAdapter <-->|"HTTPS"| LLMCloud

    N3 --> ToolGW
    ToolGW --> TPrice & THist & TQuant & TAnom & TRep
    TPrice --> RedisRO
    THist & TQuant & TAnom --> CHRO

    N1 & N3 & N5 -->|"Checkpoint State & Audit Trail"| PGState
```

