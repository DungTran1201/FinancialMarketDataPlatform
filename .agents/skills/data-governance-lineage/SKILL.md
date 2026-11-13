---
name: data-governance-lineage
description: "Define dataset ownership, metadata, lineage, access classes, retention, schema lifecycle and provenance across financial data products."
---

# Skill: Data Governance, Ownership & Lineage (`SKILL-018`)

## 1. Description

Define dataset ownership, metadata, lineage, access classes, retention, schema lifecycle, and provenance across financial data products.

## 2. Trigger Conditions

- Use for new datasets, event/schema changes, data catalog/dictionary updates, retention policies, data access controls, audits, or Agent/BI data provenance.
- Invoked by Agent role `data-quality-governance-engineer` (`.agents/agents/data-quality-governance-engineer.md`).

## 3. Authoritative Inputs

- `AGENTS.md` and target directory `README.md`
- `docs/specifications/data-contracts.md`, `data-dictionary.md`, and `data-requirements.md`
- `.agents/config/data-platform-boundaries.yaml`
- `models/domain/`, `models/security/`, and `src/agent/tools/contracts.py` (`ToolProvenanceMetadata`)

## 4. Preconditions

1. Target directory `README.md` has been read in full.
2. Data owner/steward, business purpose, classification, dataset grain, natural key, and lifecycle stage have been identified.

## 5. Execution Procedure

1. Create or update dataset metadata with name, description, owner role, purpose, grain, primary/natural key, schema, and domain.
2. Document units, `Decimal` precision, nullability, `exchange_event_time`, `ingested_at`, UTC timezone semantics, and source-of-truth precedence.
3. Map end-to-end lineage from exchange source through `EventEnvelopeV1`/Kafka topic, raw Bronze storage, Silver/Gold transforms, and Backend API/BI/Agent Tool Gateway consumers.
4. Record quality assertions, freshness targets, retention TTL, archive, deletion, and recovery policies.
5. Map data classification to least-privilege access controls, service identities, and audit requirements.
6. Govern schema versions and deprecation windows with consumer impact and compatibility reviews.
7. Preserve `ToolProvenanceMetadata` in analytical and Agent outputs, including backing store and requested time window.
8. Synchronize `docs/specifications/data-dictionary.md`, `models/domain/`, and diagrams, then run `tools/validators/run_all.py`.

## 6. Output Artifacts

- Dataset dictionary/catalog entries (`docs/specifications/data-dictionary.md`), canonical domain models (`models/domain/`), lineage maps, retention metadata, and governance review records.

## 7. Validation

```powershell
python tools/validators/run_all.py
python -m unittest discover -s tests -v
```

## 8. Failure Handling

- Mark missing ownership or lineage facts as `[OPEN QUESTION]` and block promotion to `APPROVED` or `BASELINED` until resolved.

## 9. Restrictions

- Do not invent dataset owners or unverified lineage links.
- Do not place secrets or private user data into documentation or sample payloads.
- Do not claim automated catalog lineage where only a static diagram exists.

## 10. Related Skills

- `data-platform-discovery`
- `financial-data-quality`
- `lakehouse-medallion`
- `analytics-engineering-dbt-clickhouse`

