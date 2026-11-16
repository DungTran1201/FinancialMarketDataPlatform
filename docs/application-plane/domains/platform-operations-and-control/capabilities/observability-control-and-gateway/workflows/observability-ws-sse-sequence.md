---
doc_id: DIAG-APP-OPS-SEQ-001
title: "Sequence Diagram: WebSocket & SSE Live Observability Subscription"
doc_type: diagram
plane: application-plane
scope_level: capability
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: IN_REVIEW
implementation_status: IMPLEMENTED
version: "2.0.0"
owner_role: fullstack-engineer
accountable_role: devops-sre
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: false
  authoritative_source:
    - "docs/application-plane/domains/platform-operations-and-control/capabilities/observability-control-and-gateway/use-cases/uc-ops-001-dashboard-live-probe-and-streams.md"
related_docs:
  - CAP-APP-OPS-UC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: fullstack-engineer
    summary: "Rendered WebSocket and SSE streaming subscription handshake, live trace push, heartbeat, and cleanup."
---

# Sequence Diagram: WebSocket & SSE Live Observability Subscription

## 1. Diagram Metadata

| Field | Value |
|---|---|
| **Diagram ID** | `DIAG-APP-OPS-SEQ-001` |
| **Title & Purpose** | WebSocket `/ws/v1/observability/stream` & SSE `/api/v1/observability/stream` Protocol |
| **Owner Role & Scope** | `fullstack-engineer / CAP-APP-OPS-001` |
| **Authoritative Source** | [uc-ops-001-dashboard-live-probe-and-streams.md](../use-cases/uc-ops-001-dashboard-live-probe-and-streams.md) (`CAP-APP-OPS-UC-001`) |
| **Notation** | `Mermaid sequenceDiagram` (`UML 2.5.1`) |
| **Version & Status** | `2.0.0 — IN_REVIEW` |

## 2. Diagram

```mermaid
sequenceDiagram
    autonumber
    participant UI as Dashboard / DataFlow UI
    participant OBS as Observability Router
    participant TR as trace_registry

    UI->>OBS: Connect WS /ws/v1/observability/stream (or GET /stream SSE)
    OBS->>TR: subscribe(loop) -> (sub_id, queue)
    OBS-->>UI: Initial {"type": "snapshot", "overview": ...}
    loop Every Trace Event or 3.0s Timeout
        alt New Trace Published
            TR->>OBS: queue.put(trace_item)
            OBS-->>UI: {"type": "trace", "trace": ...}
        else Timeout (3.0s WS / 2.5s SSE)
            OBS-->>UI: {"type": "heartbeat", "overview": ...}
        else Client Keepalive (WS only)
            UI->>OBS: {"type": "ping", "timestamp": ...}
            OBS-->>UI: {"type": "pong", "timestamp": ...}
        end
    end
    UI-xOBS: Disconnect
    OBS->>TR: unsubscribe(sub_id)
```

## 3. Legend

- **Queue Isolation**: Each connected subscriber receives its own `asyncio.Queue`; `finally` guarantees cleanup on client disconnect.
