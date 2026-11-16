---
name: data-governance-lineage
description: Dataset ownership, end-to-end lineage, retention policies, and schema lifecycle.
---

# Skill: Data Governance, Ownership & Lineage (`SKILL-018`)

## 1. Description

Define dataset ownership, metadata, end-to-end lineage, access classes, retention TTL, schema lifecycle, and `ToolProvenanceMetadata` across financial data products.

## 2. Trigger Conditions

- New datasets, event/schema changes, data catalog/dictionary updates, retention policies, data access controls, audits, or Agent/BI data provenance (`data-quality-governance-engineer`).

## 3. Authoritative Inputs

- `AGENTS.md`, `docs/data-plane/shared-contracts/data-contract.yaml`, `docs/data-plane/domains/lakehouse-analytics/capabilities/medallion-lakehouse-and-quality-gates/`, `docs/intelligence-plane/shared-contracts/tool-contracts.yaml`, `.agents/config/data-platform-boundaries.yaml`, `src/lakehouse/catalog/lineage.py`, `src/intelligence/tools/contracts.py` (`ToolProvenanceMetadata`).

## 4. Preconditions

1. Owning capability `capability.yaml` read; data owner/steward, business purpose, classification, dataset grain, natural key, and lifecycle stage identified.

## 5. Execution Procedure

1. Create or update dataset metadata in `data-contract.yaml` and capability `data/data-model.md` with name, description, owner role, purpose, grain, primary/natural key, schema, and domain.
2. Document units, `Decimal` precision, nullability, `exchange_event_time`, `ingested_at`, UTC timezone semantics, and source-of-truth precedence.
3. Map end-to-end lineage from exchange source through `EventEnvelopeV1`/Kafka topic, raw Bronze storage, Silver/Gold transforms, and Backend API/BI/Agent Tool Gateway consumers.
4. Record quality assertions, freshness targets, retention TTL, archive, deletion, and recovery policies.
5. Map data classification to least-privilege access controls, service identities, and audit requirements.
6. Govern schema versions and deprecation windows with consumer impact and compatibility reviews.
7. Preserve `ToolProvenanceMetadata` in analytical and Agent outputs, including backing store and requested time window.
8. Synchronize `docs/data-plane/shared-contracts/data-contract.yaml`, capability `data/` docs, and derived DFD diagrams, then run `scripts/docs/validate_docs.py`.

## 6. Output Artifacts

- Updated dataset contracts (`data-contract.yaml`), capability data models (`data/data-model.md`), lineage diagrams, retention metadata, and governance review records.

## 7. Validation

```powershell
python scripts/docs/validate_docs.py
python -m pytest tests/contract/ -v
```

## 8. Failure Handling

- Mark missing ownership or lineage facts as `[OPEN]` in `capability.yaml` and block transition to `APPROVED` until resolved.

## 9. Restrictions

- Do not invent dataset owners or unverified lineage links.
- Do not place secrets or private user data into documentation or sample payloads.
- Do not claim automated catalog lineage where only a static diagram exists.

## 10. Related Skills

- `data-platform-discovery`
- `financial-data-quality`
- `lakehouse-medallion`
- `analytics-engineering-dbt-clickhouse`
