---
doc_id: DIAG-INT-C4-001
title: "Intelligence Plane C4 Container Diagram"
doc_type: diagram
plane: intelligence-plane
scope_level: plane
status: DRAFT
implementation_status: SIMULATED
version: "2.0.0"
owner_role: ai-engineer
accountable_role: system-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/intelligence-plane/architecture/intelligence-architecture.md"
    - "src/intelligence/orchestrator/graph.py"
    - "src/serving/infrastructure/runtime.py"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Created Intelligence Plane C4 Container diagram distinguishing AS-IS inline execution from TARGET isolated worker."
---

# Intelligence Plane C4 Container Diagram

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-C4-001` |
| **Purpose** | Visualize Intelligence Plane containers, cross-plane boundaries, and AS-IS vs TARGET runtime wiring. |
| **Scope & Owner** | `plane` (`intelligence-plane`) / `ai-engineer` |
| **Authoritative Source** | [intelligence-architecture.md](../intelligence-architecture.md) (`INT-ARCH-001`) |
| **Notation** | Mermaid `flowchart TB` (C4 Level 2 Container View) |
| **Version & Status** | `2.0.0` / `DRAFT` (`SIMULATED`) |

```mermaid
flowchart TB
    subgraph APP["Application Plane (CAP-APP-AGT-001)"]
        API["FastAPI Agent & Reporting Routers (/api/v1/agents, /reports)"]
        RT["PlatformRuntimeContainer (In-Process DI Root AS-IS)"]
    end

    subgraph INT["Intelligence Plane (CAP-INT-ORC-001)"]
        GRAPH["MarketIntelligenceGraph (5-Node Pure Python Loop AS-IS)"]
        LLM_MOCK["DeterministicMockLLMAdapter (AS-IS Mock)"]
        LLM_EXT["External LLM Provider (TARGET)"]
        GW["ControlledToolGateway (10-Tool Whitelist & Audit)"]
        VAL["ReportValidator (Citation ID Check)"]
        WORKER["agent-worker (src/intelligence/main.py — Stub AS-IS / LangGraph TARGET)"]
    end

    subgraph DATA["Data Plane & Control Stores"]
        REDIS["Redis / HotStateProjector (In-Memory AS-IS)"]
        CH["ClickHouse / ClickHouseBatchSink (In-Memory AS-IS)"]
        ANOM["AnomalyDetector & detected_anomalies"]
        PG["PostgreSQL agent_runs & agent_tool_invocations (TARGET)"]
        KAFKA["Kafka market.anomalies.v1 (TARGET Event Trigger)"]
    end

    API -->|"Sync await AS-IS"| RT
    RT -->|"run_investigation()"| GRAPH
    GRAPH -->|"plan / synthesize AS-IS"| LLM_MOCK
    GRAPH -.->|"TARGET external call"| LLM_EXT
    GRAPH -->|"execute_tool()"| GW
    GRAPH -->|"validate_report()"| VAL
    GW -->|"Read market/freshness"| REDIS
    GW -->|"Read candles/stats/math"| CH
    GW -->|"Evaluate & append anomaly"| ANOM
    GW -->|"Write runtime.reports AS-IS"| RT
    KAFKA -.->|"TARGET event trigger"| WORKER
    WORKER -.->|"TARGET checkpoint & report"| PG
```

**Legend**: Solid arrows (`-->`) denote `AS-IS` implemented runtime paths; dashed arrows (`-.->`) denote `TARGET` unimplemented paths.

