---
doc_id: APP-OPS-INC-001
title: "Application Plane Incident & Recovery Guide"
doc_type: specification
plane: application-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: devops-sre
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/serving/api/main.py"
    - "src/serving/api/modules/iam/presentation/router.py"
related_docs:
  - APP-OPS-RUN-001
  - APP-ARCH-SEC-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: devops-sre
    summary: "Documented incident procedures for WAF false positives, rate-limit floods, SSE/WS disconnects, and container state loss."
---

# Application Plane Incident & Recovery Guide

## 1. Incident Response Playbooks (`AS-IS`)

| Incident Mode | Detection Signal | Mitigation & Honest Recovery Reality |
|---|---|---|
| **Process Restart Wipes API State** | `/agents/runs`, `/reports`, `/historical/backfill-jobs`, revoked JWT hashes empty after restart. | Re-run `/api/v1/data-platform/v01/run` or backfill/agent endpoints. Permanent fix requires Postgres/Redis wiring (`ADR-APP-0002`, `OPEN`). |
| **SSE / WS Telemetry Freeze** | UI shows disconnected/stale heartbeat; check `GET /api/v1/observability/overview` and `trace_registry` count. | Refresh SPA or reconnect `/ws/v1/observability/stream` (no backend control pause endpoint exists). |
| **IP Spoofing Rate-Limit Lockout** | Legitimate clients receive HTTP `429` from spoofed `X-Forwarded-For` collisions or attacker exhaustion. | Restarting process clears in-memory `SlidingWindowRateLimiter`; long-term fix requires trusted reverse-proxy CIDR allowlist (`APP-ARCH-SEC-001`). |
| **Suspected Key / Secret Exposure** | Hardcoded default `jwt_secret_key` left active in non-local environment. | Immediately override `JWT_SECRET_KEY` environment variable and restart all serving processes (invalidating all HS256 JWTs signed with default secret). |

## 2. Recovery Objectives Status

- Formal Application Plane RTO/RPO targets are **`OPEN`** (`[ASSUMPTION: Needs SRE & Product sign-off]`) and cannot be achieved for in-memory sessions/runs until Postgres/Redis backing is implemented.
