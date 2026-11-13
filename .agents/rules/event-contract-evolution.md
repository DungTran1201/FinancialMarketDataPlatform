# Data Rule — Event Contracts and Schema Evolution (`DATA-RULE-003`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-003` |
| **Rule Slug** | `event-contract-evolution` |
| **Trigger Scope** | `EventEnvelopeV1`, provider normalization, Kafka topics, schemas, serialization, and downstream consumers |
| **Activation Mode** | `Always Active` |
| **Status** | `BASELINED` |
| **Updated Date** | `2026-11-12` |

---

## 1. Purpose & Scope

Governs canonical event contracts (`EventEnvelopeV1`), deterministic UUIDv5 event IDs, partition keys, and schema compatibility across Kafka producers and consumers.

## 2. Mandatory Directives

1. **Canonical Envelope & Topics**: Use `EventEnvelopeV1` (`src/shared/contracts/events.py`) and approved versioned topic names (`market.raw.*.v1`, `market.anomalies.v1`, `market.dlq.v1`).
2. **Contract Completeness**: Document `schema_version`, required/optional fields, defaults, units, precision, enum values, natural key, and partition key (`{provider}:{symbol}` or `{provider}:{symbol}:{interval}`).
3. **Compatibility Evaluation**: Evaluate backward/forward compatibility and mixed-version rollout before any schema change.
4. **Synchronized Updates**: Update `src/shared/contracts/events.py`, `docs/specifications/data-contracts.md`, `models/api/`, and contract tests together.

## 3. Prohibited Actions

- Do not rename, remove, or reinterpret fields in a versioned contract without an approved compatibility plan and version bump.
- Do not let provider-specific raw field naming or semantics leak into canonical downstream datasets.
- Do not reuse event IDs for distinct natural records.

## 4. Verification Mechanism

- Schema and serialization contract tests (`tests/unit/test_contracts_and_guardrails.py`) and `tools/validators/run_all.py`.

