---
name: api-contract
description: Authors OpenAPI 3.1, AsyncAPI 3.1, data contracts, and error catalogs at owning V2 scopes.
---

# Skill: API & Event Contract Specification (`SKILL-009`)

## 1. Description

Specifies versioned HTTP (`openapi.yaml`), asynchronous event (`asyncapi.yaml`), dataset (`data-contract.yaml`), and canonical error (`error-catalog.md`) contracts at owning capability `contracts/` or plane `shared-contracts/` scopes.

## 2. Trigger Conditions

- Lifecycle Stage 3 (`Specification`), `api-contract-change`, or `data-pipeline-change` (`api-architect`, `fullstack-engineer`, `data-architect`).

## 3. Authoritative Inputs

- `docs/governance/standards/api-and-event-contract-standards.md`, `docs/governance/templates/interfaces-and-data/`, `src/serving/api/` routers, `src/shared/contracts/events/market_events.py`, `src/streaming/contracts/topics.py`.

## 4. Preconditions

1. Owning `capability.yaml` or `<plane>/shared-contracts/README.md` read; single canonical owner verified and `EventEnvelopeV1` compatibility rules (`DATA-RULE-003`) checked.

## 5. Execution Procedure

1. Update canonical `openapi.yaml` (OpenAPI 3.1.0), `asyncapi.yaml` (AsyncAPI 3.1.0), `data-contract.yaml`, and `error-catalog.md` at their owning scope using `docs/governance/templates/interfaces-and-data/`.
2. Enforce `Decimal` string serialization where applicable, UTC ISO-8601 timestamps, `BoundedTimeRange`, and honest disclosure of `AS-IS` auth (`security: []` if `SEC-AUDIT-003` unimplemented) vs `TARGET` RBAC.
3. Reference canonical contract files from capability prose and sequence diagrams instead of copying schemas inline into Markdown.
4. Run `python scripts/docs/validate_docs.py` and contract tests (`tests/contract/`).

## 6. Output Artifacts

- `<capability>/contracts/{openapi.yaml,data-contract.yaml,error-catalog.md}` and `<plane>/shared-contracts/{asyncapi.yaml,data-contract.yaml,tool-contracts.yaml}`.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/contract/ -v
```

## 8. Failure Handling

- Tag unconfirmed payload fields, planned endpoints, or auth gaps as `[OPEN]` / `BLOCKED`; fix all OpenAPI/AsyncAPI/YAML validator errors.

## 9. Restrictions

- Never break existing `/api/v1` routes or `.v1` Kafka topic contracts silently; never recreate retired `models/api/` or `docs/product/08-api/`.

## 10. Related Skills

- `domain-modeling`, `kafka-event-streaming`, `security-threat-modeling`
