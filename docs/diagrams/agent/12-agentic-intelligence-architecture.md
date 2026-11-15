# Diagram 12: Agentic Intelligence Architecture (`DIAG-C4-012`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-C4-012` (legacy `DOCS-002` alias: `DIAG-COMP-012`) |
| **Title** | Agentic Intelligence Architecture (5-Node LangGraph + 10-Tool Gateway) |
| **Diagram Category** | `docs/diagrams/agent/` |
| **Notation / Mermaid Type** | `Mermaid (flowchart TB)` |
| **Status** | `IMPLEMENTED` / `PARTIALLY_IMPLEMENTED` (5-node graph & 10-tool gateway implemented in `src/intelligence/`; standalone `agent-worker` daemon loop `PROP-APP-002`, Kafka anomaly consumer & `fmdp_agent_ro` SQL user `[PLANNED]`) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/06-agentic-intelligence-architecture.md` |
| **Canonical Model Reference** | `models/architecture/components.yaml`, `models/interaction/interactions.yaml` |
| **Related Artifact IDs** | `COMP-005`, `COMP-019`, `API-008`, `API-009`, `PROP-APP-002` |

## Architectural Explanation

The **Agentic Intelligence Architecture** illustrates how the **Intelligence Plane** (`src/intelligence/`, plus `agent-worker` container definition) executes **MarketIntelligenceGraph**:
- **Trigger Entrypoints**:
  1. **On-Demand Analysis (`[IMPLEMENTED]`)**: Triggered via `POST /api/v1/agents/runs` (`API-008`) executing `MarketIntelligenceGraph` + `ControlledToolGateway`.
  2. **Event-Triggered Investigation (`[PLANNED]` Daemon Consumer)**: Target integration consuming `market.anomalies.v1` through a deduplication cooldown filter.
- **Stateful 5-Node Orchestrator (`MarketIntelligenceGraph`)**:
  - `Intake & Guardrail Validator` $\rightarrow$ `Investigation Planner` $\rightarrow$ `Tool Gateway Executor` $\rightarrow$ `Evidence Verifier` $\rightarrow$ `Structured Report Synthesizer`.
  - Standalone `agent-worker` CLI loop (`src/intelligence/main.py`) is currently a stub (`PROP-APP-002`); active runs store evidence trails in `PlatformRuntimeContainer.agent_runs` (with PostgreSQL persistent worker checkpointing & `fmdp_agent_ro` ClickHouse SQL user `[PLANNED]`).

```mermaid
flowchart TB
    subgraph Triggers["1. Agent Triggering Modes"]
        UserTrigger["On-Demand Request [IMPLEMENTED]<br/>POST /api/v1/agents/runs"]
        AnomalyStream["Event-Triggered Anomaly [PLANNED Consumer]<br/>Kafka: market.anomalies.v1"]
        CooldownFilter["Cooldown Gate [PLANNED Daemon]<br/>(agent:cooldown:{symbol}:{detector})"]
    end

    subgraph AgentService["2. Intelligence Plane: 5-Node Orchestrator (src/intelligence/)"]
        subgraph LangGraphWorkflow["MarketIntelligenceGraph (5-Node State Graph)"]
            N1["Node 1: Intake & Guardrail Validator<br/>(Verify Scope, Time Window, Token Budget)"]
            N2["Node 2: Investigation Planner<br/>(Select Deterministic Tools)"]
            N3["Node 3: Tool Gateway Executor<br/>(Run Quant & Data Tools)"]
            N4["Node 4: Evidence Verifier<br/>(Check Provenance, Completeness & Bounds)"]
            N5["Node 5: Structured Report Synthesizer<br/>(Generate JSON Report with Citations)"]

            N1 --> N2 --> N3 --> N4
            N4 -->|"Need Additional Evidence (Max 6 Steps)"| N2
            N4 -->|"Sufficient Deterministic Evidence"| N5
        end

        LLMAdapter["LLM Adapter / Deterministic Fallback<br/>(External LLM Optional; Zero-Fake Fallback Active)"]
        ToolGW["ControlledToolGateway<br/>(10 Whitelisted Tools, Schema & Bounds, Provenance)"]
    end

    subgraph DeterministicTools["3. 10 Whitelisted Deterministic Tools (contracts.py)"]
        TPrice["get_latest_price / get_market_snapshot"]
        THist["get_historical_candles / get_market_statistics"]
        TQuant["calculate_returns / calculate_volatility / calculate_correlation"]
        TAnom["detect_anomalies / get_data_freshness"]
        TRep["generate_analysis_report"]
    end

    subgraph DataAndState["4. Persistence & Read-Only Data Sources"]
        PGState[("Runtime State / PostgreSQL [PLANNED Worker PG]<br/>agent_runs & tool_invocations")]
        RedisRO[("Redis / HotStateProjector<br/>Hot Market State")]
        CHRO[("ClickHouse / OLAP Adapter<br/>(Dedicated fmdp_agent_ro PLANNED)")]
        LLMCloud["External LLM API (Optional)"]
    end

    UserTrigger -->|"Invoke Execution"| N1
    AnomalyStream -.-> CooldownFilter -.->|"Passed Cooldown [PLANNED]"| N1

    N2 & N5 <-->|"Structured Prompt / Fallback"| LLMAdapter
    LLMAdapter <-.->|"HTTPS (When Configured)"| LLMCloud

    N3 --> ToolGW
    ToolGW --> TPrice & THist & TQuant & TAnom & TRep
    TPrice --> RedisRO
    THist & TQuant & TAnom --> CHRO

    N1 & N3 & N5 -->|"Audit Trail & Result"| PGState
```

