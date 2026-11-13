---
name: data-platform-testing-recovery
description: "Test data pipeline correctness and operational recovery, including replay, duplicates, late events, sink failure windows, backfills and cross-plane isolation."
---

# Skill: Data Platform Testing & Recovery Verification (`SKILL-020`)

## 1. Description

Test data pipeline correctness and operational recovery, including replay, duplicates, late events, sink failure windows, backfills, and cross-plane isolation.

## 2. Trigger Conditions

- Use for new or changed data pipelines, storage sinks, contracts, backfills, deployment profiles, recovery procedures, critical data-quality gates, or production-readiness reviews.
- Invoked by Agent roles `financial-data-platform-reviewer`, `qa-reviewer`, and `data-engineer`.

## 3. Authoritative Inputs

- `AGENTS.md` and target directory `README.md`
- Active Work Item (`work-items/<ID>/`), `models/testing/testing.yaml`, and `models/requirements/acceptance-criteria.yaml`
- `src/shared/contracts/events.py`, `src/agent/tools/gateway.py`, `tests/`, and `docker-compose.yml`

## 4. Preconditions

1. Target directory `README.md` has been read in full.
2. Expected delivery semantics, natural keys, freshness objectives, time windows, critical failure cases, and test safety constraints have been defined.

## 5. Execution Procedure

1. Build a test matrix across unit, contract, architectural boundary, integration, failure-injection, and recovery dimensions in `models/testing/testing.yaml`.
2. Test canonical event serialization (`EventEnvelopeV1`), schema evolution, exact `Decimal` precision, OHLCV invariants, and UTC timestamp validation.
3. Test duplicate/reordered/late events, Kafka partition key stability, sink timeouts, and crash windows around offset commit.
4. Test REST pagination, source throttling, WebSocket disconnect/reconnect, replay, and watermark consistency.
5. Test Bronze append semantics, Silver idempotent Iceberg `MERGE INTO`, Gold incremental/full-refresh equivalence, and `CRITICAL` DQ promotion blocking.
6. Test storage failure isolation, Redis -> ClickHouse transparent fallback (`ADR-005`), and cross-plane boundary enforcement (`Plane A` never imports `Plane C`).
7. Test lineage/provenance (`ToolProvenanceMetadata`), RBAC permission boundaries, and bounded Agent query limits (`ControlledToolGateway`).
8. Execute unit/architecture tests and `tools/validators/run_all.py`, recording exact pass/fail evidence.

## 6. Output Artifacts

- Updated canonical test model (`models/testing/testing.yaml`), automated test suites (`tests/`), failure-injection/recovery plans, and verification reports (`work-items/<ID>/review.md`).

## 7. Validation

```powershell
python tools/validators/run_all.py
python -m unittest discover -s tests -v
```

## 8. Failure Handling

- Preserve failing test output and reproduction steps; block release promotion (`G5_VERIFY` / `G6_RELEASE`) when critical data-loss, precision, or boundary violations remain unresolved.

## 9. Restrictions

- Do not use production secrets or live user credentials in tests.
- Do not claim unexecuted integration or recovery tests passed.

## 10. Related Skills

- `test-modeling`
- `financial-data-quality`
- `kafka-event-streaming`
- `lakehouse-medallion`
- `dataops-observability`

