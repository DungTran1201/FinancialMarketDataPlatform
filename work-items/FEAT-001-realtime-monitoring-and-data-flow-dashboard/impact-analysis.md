# Impact Analysis — FEAT-001

| Metadata | Value |
|---|---|
| **Work Item ID** | `FEAT-001` |
| **Authoring Role** | `discovery-analyst` / `architecture-modeler` |
| **Status** | `COMPLETED` |
| **Created Date** | `2026-11-15` |
| **Updated Date** | `2026-11-15` |

---

## 1. Affected Architectural Planes

- [x] Plane A — Data Plane
- [x] Plane B — Application & Control Plane
- [ ] Plane C — Intelligence Plane
- [x] Cross-Cutting — Documentation / Governance / Tooling

## 2. Affected Subsystems & Directories

| Subsystem | Path | Impact Level (`NONE`/`LOW`/`MEDIUM`/`HIGH`) | Description |
|---|---|---|---|
| Shared Observability | `src/shared/observability/` | `HIGH` | Add `tracing.py` (`EventLifecycleTrace`, `PipelineTraceRegistry`) & expand `metrics.py` histograms/counters. |
| Streaming & Sink Introspection | `src/streaming/` | `MEDIUM` | Read-only partition/offset/lag/timeseries introspection (`kafka_broker.py`), OHLCV rollup & storage counters (`analytics_ch.py`). |
| Pipeline Orchestration | `src/lakehouse/orchestration/` | `MEDIUM` | Emit `EventLifecycleTrace` events cleanly during 12-stage execution while preserving `API-016` backward compatibility. |
| Serving Runtime & API/UI | `src/serving/` | `HIGH` | Wire `PipelineTraceRegistry`, add `/api/v1/observability/*` + SSE/WS, rewrite `/ui/data-flow` + static assets, scope CSP for `/ui/*` in `iam/presentation/router.py`. |
| Canonical Models | `models/` | `MEDIUM` | Synchronize `models/api/api.yaml`, `models/ux/ux.yaml`, `models/requirements/*.yaml`, `models/testing/testing.yaml`. |
| Documentation & Diagrams | `docs/` | `MEDIUM` | Update `api-specification.md`, `11-ux/`, `01-realtime-data-flow-ui-architecture.md`, and add `docs/product/13-operations/monitoring.md`. |
| Automated Tests | `tests/` | `HIGH` | Add `tests/integration/test_realtime_observability_dashboard.py` verifying traces, parallel E2E math, CSP, SSE, and rollups. |

## 3. Backward Compatibility & Risk Assessment

- **Risk 1 — Breaking Clean Architecture Boundary (`TC-006`)**: Mitigated by locating tracing contracts in `src/shared/observability/` and exposing read/action facades exclusively via `PlatformRuntimeContainer` in `src/serving/infrastructure/runtime.py`.
- **Risk 2 — Loosening Security CSP (`test_security_and_defense.py`)**: Mitigated by preserving `default-src 'none'` on API endpoints and granting `/ui/*` a strict `'self'` CSP with external static assets (`/ui/assets/*`) and zero inline `<script>`.
- **Risk 3 — Prometheus Cardinality Explosion (`DATA-RULE-010`)**: Mitigated by keeping `event_id` and `correlation_id` strictly inside bounded `PipelineTraceRegistry` (`maxlen=2000`) and permitting only bounded labels (`stage`, `mode`, `path`, `status`) on Prometheus metrics.
- **Risk 4 — Breaking `API-016` (`TC-011`)**: Mitigated by leaving `step_realtime_tick_and_collect_telemetry()` response keys intact while tagging synthetic ticks explicitly and isolating clean telemetry under `/api/v1/observability/*`.

