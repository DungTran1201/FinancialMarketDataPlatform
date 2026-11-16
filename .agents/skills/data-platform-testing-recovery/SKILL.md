---
name: data-platform-testing-recovery
description: Pipeline replay, deduplication, late-event, backfill, and fault-recovery tests.
---

# Skill: Data Platform Testing & Recovery Verification (`SKILL-020`)

## 1. Description

Test data pipeline correctness and operational recovery, including replay, duplicates, late events, sink failure windows, backfills, and cross-plane isolation.

## 2. Trigger Conditions

- New or changed data pipelines, storage sinks, contracts, backfills, deployment profiles, recovery procedures, or production-readiness reviews (`financial-data-platform-reviewer`, `qa-reviewer`, `data-engineer`).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/data-plane/operations/test-plan.md`, owning `capability.yaml`, `<capability>/quality/{test-scenarios.md,test-cases.yaml,traceability.yaml}`, `src/shared/contracts/events/market_events.py`, `src/intelligence/tools/gateway.py`, `tests/`, `docker-compose.yml`.

## 4. Preconditions

1. Owning `capability.yaml` and `quality/test-cases.yaml` read; expected delivery semantics, natural keys, freshness objectives, time windows, and failure cases defined.

## 5. Execution Procedure

1. Maintain a test matrix across unit, contract, architectural boundary, integration, failure-injection, and recovery dimensions in `<capability>/quality/test-cases.yaml` and `test-scenarios.md`.
2. Test canonical event serialization (`EventEnvelopeV1`), schema evolution, exact `Decimal` precision, OHLCV invariants, and UTC timestamp validation.
3. Test duplicate/reordered/late events, Kafka partition key stability, sink timeouts, and crash windows around offset commit.
4. Test REST pagination, source throttling, WebSocket disconnect/reconnect, replay, and watermark consistency.
5. Test Bronze append semantics, Silver idempotent Iceberg `MERGE INTO`, Gold incremental/full-refresh equivalence, and `CRITICAL` DQ promotion blocking.
6. Test storage failure isolation, Redis -> ClickHouse transparent fallback, and cross-plane boundary enforcement (`Plane A` never imports `Plane C`).
7. Test lineage/provenance (`ToolProvenanceMetadata`), RBAC permission boundaries, and bounded Agent query limits (`ControlledToolGateway`).
8. Execute `pytest tests/ -v` and `scripts/docs/validate_docs.py`, recording exact pass/fail evidence and execution environment in `quality/traceability.yaml`.

## 6. Output Artifacts

- Updated `<capability>/quality/{test-cases.yaml,test-scenarios.md,traceability.yaml}`, automated test suites (`tests/`), failure-injection/recovery plans, and verification evidence.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/ -v
```

## 8. Failure Handling

- Preserve failing test output and reproduction steps; block `QG-6-VERIFY` / `implementation_status: VERIFIED` when critical data-loss, precision, or boundary violations remain unresolved.

## 9. Restrictions

- Do not use production secrets or live user credentials in tests.
- Do not claim unexecuted integration or live-cluster recovery tests passed.

## 10. Related Skills

- `test-modeling`
- `financial-data-quality`
- `kafka-event-streaming`
- `lakehouse-medallion`
- `dataops-observability`
