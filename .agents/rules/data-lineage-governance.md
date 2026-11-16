# Data Rule — Data Ownership, Metadata, Lineage and Retention (`DATA-RULE-009`)

| Metadata | Value |
|---|---|
| **Rule ID** | `DATA-RULE-009` |
| **Rule Slug** | `data-lineage-governance` |
| **Trigger Scope** | Dataset creation, schema/model changes, data serving, backfills, retention, and governance |
| **Activation Mode** | `Always Active` |
| **Status** | `APPROVED` |
| **Updated Date** | `2026-11-16` |

---

## 1. Purpose & Scope

Establishes end-to-end dataset ownership, data dictionary completeness, source-to-consumer lineage, retention policies, and provenance tracking (`ToolProvenanceMetadata`) across all financial data products.

## 2. Mandatory Directives

1. **Dataset Metadata**: Record dataset owner, purpose, grain, primary/natural keys, schema, units, Decimal precision, UTC timestamp semantics, quality rules, and access classification in `docs/data-plane/shared-contracts/data-contract.yaml` and owning capability `data/` models.
2. **End-to-End Lineage**: Trace `Provider Source -> EventEnvelopeV1 / Kafka Topic -> Storage Sink / Table -> Spark / dbt Model -> Backend API / Superset BI / Agent Tool Gateway`.
3. **Retention & Lifecycle**: Define TTL, archival, Iceberg snapshot expiry, backup, and restore policies per storage engine.
4. **Analytical & Agent Provenance**: Attach `ToolProvenanceMetadata` (`invocation_id`, `tool_name`, `source_store`, `symbol`, `window_start`, `window_end`, `row_count`, `executed_at`) to every Agent tool output.

## 3. Prohibited Actions

- Do not invent undocumented dataset owners or unverified lineage links.
- Do not delete or expire historical data without retention and recovery impact analysis.
- Do not expose private user, credential, or secret data in analytical datasets or logs.

## 4. Verification Mechanism

- `docs/data-plane/shared-contracts/data-contract.yaml`, capability `data/data-model.md` and `quality/traceability.yaml` inspection, provenance contract tests (`tests/contract/test_contracts_and_guardrails.py`), and `scripts/docs/validate_docs.py` (`tools/validators/run_all.py`).
