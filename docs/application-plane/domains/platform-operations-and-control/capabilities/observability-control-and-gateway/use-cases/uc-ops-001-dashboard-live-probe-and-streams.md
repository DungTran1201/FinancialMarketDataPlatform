---
doc_id: CAP-APP-OPS-UC-001
title: "Use Case UC-OPS-001: View Dashboard Overview, Live Infra Probe & Subscribe to Streams"
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
    - "frontend/src/modules/dashboard/DashboardModule.ts"
related_docs:
  - CAP-APP-OPS-REQ-001
  - DIAG-APP-OPS-SEQ-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented Dashboard overview fetch, WS/SSE live telemetry subscription, /live/probe, and static UI defect."
---

# Use Case UC-OPS-001: View Dashboard Overview, Live Infra Probe & Subscribe to Streams

## 1. Actors & Preconditions

- **Actors**: Platform Operator (`#/dashboard`), External Prometheus Scraper (`/metrics`).

## 2. Main Flow & UI Defects

1. Opening `#/dashboard` fetches `GET /api/v1/observability/{overview,storage,latency}` via `ObservabilityService` (`normalizeOverviewPayload`).
2. Client opens `WS /ws/v1/observability/stream` (`ws-client.ts`) receiving initial `snapshot`, live `trace` deltas, `3.0s` `heartbeat`, and responding to `ping` -> `pong` (falls back/complements with SSE `/observability/stream`).
3. Clicking Live Infra Probe invokes `POST /api/v1/observability/live/probe` (`fetch_binance=true|false`), probing 5 Compose TCP ports and optionally fetching Binance REST candles.
4. **AS-IS UI Anomalies**: Core Stores card displays hardcoded `"5/5 Connected"` regardless of `/live/probe` results (`COMPAT-005`); `MainLayout` `LIVE/DEMO` toggle does not toggle API parameters.
