---
doc_id: CAP-APP-CAT-DM-001
title: "Logical Data Model: Monitored Instruments Registry"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-CAT-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "deploy/postgres/init/01_schema.sql"
    - "src/serving/api/modules/platform_config/domain/ports.py"
related_docs:
  - CAP-APP-CAT-DB-001
  - DIAG-APP-CAT-ERD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Defined logical entity for MonitoredInstrument and reconciled AS-IS dict vs Postgres schema drift."
---

# Logical Data Model: Monitored Instruments Registry

## 1. Logical Entity (`MonitoredInstrument`)

- **`MonitoredInstrumentConfig`** (`AS-IS` in memory): `(provider, symbol, enabled_streams, is_active)`. Keyed solely by `symbol` in `runtime.monitored_instruments`.
- **`monitored_instruments`** (`TARGET` in `01_schema.sql`): Adds `instrument_id UUID`, `base_asset`, `quote_asset`, `status CHECK('TRADING', 'HALTED', 'INACTIVE')`, JSONB `enabled_streams`, `updated_at`, with `UNIQUE(provider, symbol)`.

## 2. Logical Model Drift (`OPEN`)

- Target `status` enum (`TRADING`/`HALTED`/`INACTIVE`) vs `AS-IS` boolean `is_active`; runtime omits `base_asset`/`quote_asset` fields.
