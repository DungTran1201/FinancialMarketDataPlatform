---
doc_id: CAP-APP-CAT-DB-001
title: "Physical Database Design: Postgres `monitored_instruments`"
doc_type: specification
plane: application-plane
scope_level: capability
domain: market-experience-and-catalog
capability_id: CAP-APP-CAT-001
status: IN_REVIEW
implementation_status: NOT_IMPLEMENTED
version: "2.0.0"
owner_role: database-architect
accountable_role: fullstack-engineer
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "deploy/postgres/init/01_schema.sql"
related_docs:
  - CAP-APP-CAT-DM-001
  - DIAG-APP-CAT-ERD-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: database-architect
    summary: "Documented PostgreSQL monitored_instruments DDL, constraints, and unwired status."
---

# Physical Database Design: Postgres `monitored_instruments`

## 1. Physical Table Schema (`deploy/postgres/init/01_schema.sql` — Unwired `AS-IS`)

| Column | Type & Constraints | Purpose |
|---|---|---|
| `instrument_id` | `UUID PRIMARY KEY DEFAULT gen_random_uuid()` | Surrogate identifier |
| `provider` | `TEXT NOT NULL` | Exchange venue (`binance`) |
| `symbol` | `TEXT NOT NULL` | Trading pair (`BTCUSDT`); `UNIQUE(provider, symbol)` |
| `base_asset` | `TEXT NOT NULL` | Base currency (`BTC`) |
| `quote_asset` | `TEXT NOT NULL` | Quote currency (`USDT`) |
| `status` | `TEXT NOT NULL CHECK (status IN ('TRADING', 'HALTED', 'INACTIVE'))` | Exchange operational status |
| `enabled_streams` | `JSONB NOT NULL DEFAULT '["trade","kline_1m","ticker"]'` | Subscribed stream set |
| `updated_at` | `TIMESTAMPTZ NOT NULL DEFAULT NOW()` | Last config change |

## 2. Migration & Rollback Note

- Initialized once by Docker Compose Postgres entrypoint (`01_schema.sql`); zero application SQL driver queries exist today (`NOT_IMPLEMENTED`).
