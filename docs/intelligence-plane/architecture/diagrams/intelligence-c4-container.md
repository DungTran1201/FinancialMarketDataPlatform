---
doc_id: DIAG-INT-C4-001
title: "C4 Container Diagram: Intelligence Plane (AS-IS In-Process vs TARGET Worker)"
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
    - "docs/intelligence-plane/architecture/agent-runtime-architecture.md"
related_docs:
  - INT-ARCH-ROOT-001
  - INT-ARCH-001
  - INT-ARCH-RT-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: ai-engineer
    summary: "Rendered C4 Level 2 container topology distinguishing AS-IS in-process execution inside PlatformRuntimeContainer from TARGET isolated agent-worker."
---

# C4 Container Diagram: Intelligence Plane

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-INT-C4-001` |
| **Title & Purpose** | C4 Level 2 Container View showing Intelligence Plane containers, external stores, and `AS-IS` vs `TARGET` process boundaries |
| **Owner Role & Scope** | `ai-engineer / intelligence-plane` |
| **Authoritative Source** | [intelligence-architecture.md](../intelligence-architecture.md) (`INT-ARCH-001`) |
| **Notation** | `Mermaid flowchart TB` (`C4 Level 2 Container`) |
| **Version & Status** | `2.0.0 — DRAFT` |

## 2. Diagram

```mermaid
flowchart TB
    app_api["Application Plane: agent_api & reporting routers (Port 8000 / 8006)"]
    kafka_anom["Data Plane: Kafka market.anomalies.v1 (NOT CONSUMED AS-IS)"]

    subgraph plane_c_asis["Intelligence Plane AS-IS (Inside PlatformRuntimeContainer Process)"]
        graph_py["MarketIntelligenceGraph (5-Node Pure Python Loop)"]
        mock_llm["DeterministicMockLLMAdapter (Mock Planner & Synthesizer)"]
        gw["ControlledToolGateway (10-Tool Firewall & Audit Log)"]
        val["ReportValidator (invocation_id Check)"]
        mem_state["In-Memory Dicts: runtime.agent_runs & runtime.reports"]
    end

    subgraph plane_c_target["TARGET Isolated Container (docker-compose --profile intelligence)"]
        worker_stub["agent-worker (src/intelligence/main.py — Exits After Init AS-IS)"]
        ext_llm["External LLM Provider API (UNWIRED AS-IS)"]
        pg_db["PostgreSQL 16 (agent_runs, agent_tool_invocations — UNWIRED AS-IS)"]
    end

    dp_mem["Data Plane In-Memory Stores (HotStateProjector & ClickHouseBatchSink)"]

    app_api -->|"Inline await execute_agent_investigation() (AS-IS)"| graph_py
    app_api -.->|"TARGET: Enqueue QUEUED row"| pg_db
    kafka_anom -.->|"TARGET: Consume anomaly events"| worker_stub

    graph_py -->|"Plan & Synthesize (AS-IS)"| mock_llm
    graph_py -.->|"TARGET: HTTPS JSON Tool Call"| ext_llm
    graph_py -->|"Dispatch 10 Tools"| gw
    graph_py -->|"Validate Citations"| val

    gw -->|"Tools 1..9 Read In-Memory + Tool 8 Mutates Cooldown (AS-IS)"| dp_mem
    gw -->|"Tool 10 Writes runtime.reports (AS-IS)"| mem_state
    worker_stub -.->|"TARGET: Checkpoint State & Audit"| pg_db
```

## 3. Legend

- **Solid Container / Solid Arrows (`-->`)**: Active `AS-IS` execution path inside `PlatformRuntimeContainer` (`src/serving/infrastructure/runtime.py`).
- **Dashed Arrows (`-.->`)**: `TARGET` asynchronous worker, Kafka anomaly consumer, external LLM API, and PostgreSQL persistence not yet wired at runtime.

