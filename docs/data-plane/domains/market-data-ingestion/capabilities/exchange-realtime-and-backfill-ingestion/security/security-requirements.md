---
doc_id: CAP-DP-ING-SEC-001
title: "Security Requirements: Exchange Ingestion"
doc_type: specification
plane: data-plane
scope_level: capability
domain: market-data-ingestion
capability_id: CAP-DP-ING-001
status: DRAFT
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: security-architect
accountable_role: security-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/ingestion/providers/binance/normalizer.py"
    - "src/ingestion/application/rate_limiter.py"
related_docs:
  - CAP-DP-ING-TM-001
requirement_ids:
  - SEC-ING-001
  - SEC-ING-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: security-architect
    summary: "Defined input validation, weight throttling, and backfill RBAC requirements."
---

# Security Requirements: Exchange Ingestion

## 1. Security Controls (`SEC-ING-*`) `[REQUIRED]`

| Control ID | Security Requirement | Current Verification Status (`AS-IS`) | Target / Test Mapping |
|---|---|---|---|
| `SEC-ING-001` | Normalizer MUST reject all non-finite, negative, zero-price, malformed-timestamp, or missing-symbol frames prior to broker publish, routing failures strictly to `market.dlq.v1`. | `IMPLEMENTED` (`normalizer.py:32-221`) | `TC-ING-002` (`test_gap_recovery_and_dlq.py`) |
| `SEC-ING-002` | Manual ingestion and backfill API triggers MUST require authenticated `OPERATOR` / `ADMIN` RBAC authorization, and client credentials (`BINANCE_API_KEY`) MUST never appear in logs/docs. | **FAILING GAP (`SEC-AUDIT-003`)**: Triggers unauthenticated. `.env.example` keeps API keys blank (`SEC-ING-002` blocked in HTTP API layer). | `CAP-APP-IAM-001` remediation required (`BLOCKED`). |

## 2. Security Verification Criteria

Transitioning this specification from `DRAFT` requires `test_security_and_defense.py` coverage proving unauthenticated `POST /api/v1/historical/backfill-jobs` and `/market/ingest` fail with `401`/`403`.
