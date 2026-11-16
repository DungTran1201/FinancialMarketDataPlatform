---
doc_id: CAP-DP-LAK-RULE-001
title: "Business Rules: Data Quality Gates & Silver Deduplication"
doc_type: specification
plane: data-plane
scope_level: capability
domain: lakehouse-analytics
capability_id: CAP-DP-LAK-001
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: business-analyst
accountable_role: data-architect
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "src/lakehouse/quality/gates.py"
    - "src/lakehouse/silver/merge_engine.py"
related_docs:
  - CAP-DP-LAK-SPEC-001
requirement_ids:
  - RULE-LAK-001
  - RULE-LAK-002
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: business-analyst
    summary: "Documented exact blocking DQ rules and Silver natural-key merge rules."
---

# Business Rules: Data Quality Gates & Silver Deduplication

## 1. Blocking Data Quality Rules (`gates.py:24-79`) `[REQUIRED]`

| Rule ID | Severity | Dataset | Condition | Violation Consequence |
|---|---|---|---|---|
| `RULE-LAK-001` | `BLOCKING` (`DQ-KLINE-001..004`, `DQ-TRADE-001..003`) | `silver.market_klines`, `silver.market_trades` | `high_price >= low_price`, `open/close in [low, high]`, `price > 0`, `volume >= 0`, unique natural keys after `MERGE INTO`, non-null UTC timestamps. | Blocks Gold mart promotion (`can_promote_to_gold=False` / raises `QualityGateBlockedError`). |
| `RULE-LAK-002` | `WARNING` (`DQ-KLINE-005`) | `silver.market_klines` | Batch freshness lag within SLA threshold. | Records warning without blocking Gold promotion. |

## 2. Quantized Silver Deduplication Rule

Klines deduplicate on `(provider, symbol, interval, open_time)` keeping latest `exchange_event_time`; trades deduplicate on `(provider, symbol, trade_id)` keeping latest `ingested_at` (`merge_engine.py:31-51`). Note: `pipeline.py:348,351,354` supplies a `Path` object to `parquet_path` when returning zero-row blocked Gold results.
