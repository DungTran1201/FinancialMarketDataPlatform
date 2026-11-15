---
name: api-contract
description: REST, WebSocket, SSE, and Kafka contracts in models/api/ and docs/product/08-api/.
---

# Skill: API & Event Contract Specification (`SKILL-009`)

## 1. Description

Specifies versioned REST, WebSocket, SSE, and Kafka event contracts (`API-###`, `EVT-###`) in `models/api/`, `docs/product/08-api/`, and `docs/specifications/`.

## 2. Trigger Conditions

- Phase `08-api` or API/WebSocket/SSE/event contract changes (`api-architect`).

## 3. Authoritative Inputs

- `models/api/api.yaml`, `models/api/integrations.yaml`, `models/data-platform/events.yaml`, `docs/specifications/api-specification.md`, `data-contracts.md`, `src/shared/contracts/events/market_events.py`, `docs/templates/api/`.

## 4. Preconditions

1. Target `README.md` read; versioned endpoint/topic semantics and `EventEnvelopeV1` compatibility rules (`DATA-RULE-003`) verified.

## 5. Execution Procedure

1. Update `models/api/api.yaml`, `models/api/integrations.yaml`, and `models/data-platform/events.yaml` first with `API-###` and `EVT-###` IDs, schemas, status codes, and RBAC scopes.
2. Enforce `Decimal` string/number serialization, UTC ISO-8601 timestamps, `BoundedTimeRange`, and backward-compatible schema evolution.
3. Synchronize `docs/product/08-api/` and `docs/specifications/` using `docs/templates/api/`.
4. Update derived topology/sequence diagrams in `docs/diagrams/api/` and `docs/diagrams/sequence/`, then run `python tools/validators/run_all.py`.

## 6. Output Artifacts

- `models/api/*.yaml`, `docs/product/08-api/*.md`, `docs/diagrams/api/*.md`.

## 7. Validation

```powershell
python tools/validators/run_all.py
```

## 8. Failure Handling

- Tag unconfirmed payload fields or rate-limit quotas as `[OPEN QUESTION]`; fix all validator errors.

## 9. Restrictions

- Never introduce breaking changes on an existing `/api/v1` route or `.v1` Kafka topic without a version bump; never expose internal storage schemas directly.

## 10. Related Skills

- `domain-modeling`, `kafka-event-streaming`, `security-threat-modeling`
