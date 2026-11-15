# Diagram 13: Agent Workflow Sequence Diagram (`DIAG-SEQ-013`)

| Diagram Metadata | Value |
|---|---|
| **Diagram ID** | `DIAG-SEQ-013` |
| **Title** | Agent Workflow Sequence Diagram |
| **Diagram Category** | `docs/diagrams/agent/` |
| **Notation / Mermaid Type** | `Mermaid (sequenceDiagram)` |
| **Status** | `IMPLEMENTED` / `PARTIALLY_IMPLEMENTED` (in-process 5-node flow & 10 tools active; async Kafka trigger & standalone PG queue worker `[PLANNED]`) |
| **Version** | `1.1.0` |
| **Authoritative Document Reference** | `docs/architecture/06-agentic-intelligence-architecture.md` |
| **Canonical Model Reference** | `models/interaction/interactions.yaml`, `models/process/processes.yaml` |
| **Related Artifact IDs** | `API-008`, `API-009`, `COMP-005`, `TC-005` |

## Architectural Explanation

The **Agent Workflow Sequence Diagram** traces the execution of an Agent analysis run through the 5-node `MarketIntelligenceGraph` and 10-tool `ControlledToolGateway` (`contracts.py`), highlighting how **every quantitative figure is computed deterministically** by validated Python/OLAP tools (with per-tool timeouts `1.5s`–`8.0s` and period/row limits) while external LLM synthesis and standalone PostgreSQL worker queue consumption are optional / `[PLANNED]` enhancements.

```mermaid
sequenceDiagram
    autonumber
    actor Trigger as Analyst (POST /api/v1/agents/runs) or Planned Kafka Trigger
    participant API as Agent API Router (src/serving/api/modules/agent_api/)
    participant State as Runtime State / PostgreSQL [PLANNED Worker PG]
    participant Graph as MarketIntelligenceGraph (5 Nodes)
    participant LLM as LLM Adapter / Deterministic Fallback
    participant GW as ControlledToolGateway (10 Approved Tools)
    participant Quant as Deterministic Quant Engine (ClickHouse / Redis)

    Trigger->>API: Submit Analysis Request (BTCUSDT, prompt_summary, Idempotency-Key)
    API->>Graph: Execute Node 1..Node 5 workflow (Async standalone queue PLANNED)
    Graph->>Graph: Node 1 (Intake): Validate symbol, time bounds & token budget

    loop Bounded Tool Planning & Execution Loop (Max 6 Iterations)
        Graph->>LLM: Node 2 (Planner): Select whitelisted tools from state
        LLM-->>Graph: ToolCallRequests: [get_market_snapshot, calculate_volatility, get_data_freshness]

        par Node 3 Execute Validated Deterministic Tools via Gateway
            Graph->>GW: Invoke calculate_volatility(symbol='BTCUSDT', window='24h')
            GW->>GW: Enforce contracts.py policy (max_periods<=720, timeout=5.0s)
            GW->>Quant: Query klines & compute exact realized volatility
            Quant-->>GW: ToolExecutionEnvelope {data, provenance_metadata}
            GW-->>Graph: Verified Volatility Result + Invocation ID
        and
            Graph->>GW: Invoke get_data_freshness(symbol='BTCUSDT')
            GW->>GW: Enforce policy (max_rows=1, timeout=3.0s)
            GW->>Quant: Check Redis & ClickHouse latest timestamps
            Quant-->>GW: ToolExecutionEnvelope {is_stale, lag_ms, provenance}
            GW-->>Graph: Verified Freshness Result + Invocation ID
        end

        Graph->>Graph: Node 4 (Verifier): Verify tool evidence & completeness
    end

    Graph->>LLM: Node 5 (Synthesizer): Generate StructuredAnalysisReport from evidence
    LLM-->>Graph: Structured Report (citing exact tool invocation IDs)
    Graph->>State: Store MarketIntelligenceState (visited_nodes, evidence_trail, final_report)
    API-->>Trigger: 202 Accepted ({data: {run_id, status, tool_calls_executed}})
```

