---
doc_id: CAP-APP-OPS-UC-002
title: "Use Case UC-OPS-002: Inspect 12-Node Data Flow DAG, Traces & Trigger Simulation"
doc_type: specification
plane: application-plane
scope_level: use-case
domain: platform-operations-and-control
capability_id: CAP-APP-OPS-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/gateway/observability.py"
    - "src/serving/infrastructure/runtime.py"
    - "frontend/src/modules/data-flow/DataFlowModule.ts"
related_docs:
  - CAP-APP-OPS-REQ-001
  - DIAG-APP-OPS-FLOW-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented DataFlowModule DAG inspection, trace timeline drilldown, Kafka lag view, and demo action triggers."
---

# Use Case UC-OPS-002: Inspect 12-Node Data Flow DAG, Traces & Trigger Simulation

## 1. Main Inspection & Simulation Flows

1. Opening `#/data-flow` calls `GET /observability/topology`, `/kafka`, `/storage`, `/traces` -> displays 12 topological nodes (`exchange_source` -> `consumers_down`), parallel branches (`parallel_hot`, `parallel_olap`, `parallel_lakehouse`), and recent event traces.
2. Selecting a trace calls `GET /api/v1/observability/traces/{event_id}` (`404` if evicted from ring buffer), rendering timestamps `t0..t9` and branch latencies.
3. Operator triggers simulation via `POST /api/v1/observability/demo/emit` with `action` (`emit_batch` | `inject_dlq` | `flush_lakehouse` | `run_full_pipeline`).
4. **Gaps**: `PipelineDag.ts` embeds static SVG badges (`COMPAT-006`); `setStreamControl()` targets unimplemented `/stream/control` (`404`, `COMPAT-004`); `/demo/emit` is unauthenticated (`SEC-AUDIT-003`).

## 2. Exception Flows & Security Preconditions

- **`404` Evicted Trace**: Older events rotated out of `trace_registry` return `404`.
- **Target Auth**: Enforce `operator`/`admin` JWT verification before executing `/demo/emit`.
