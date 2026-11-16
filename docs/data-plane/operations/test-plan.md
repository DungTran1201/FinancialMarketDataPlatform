---
doc_id: DP-QA-PLAN-001
title: "Data Plane Verification Test Plan"
doc_type: specification
plane: data-plane
scope_level: plane
status: IN_REVIEW
implementation_status: PARTIALLY_IMPLEMENTED
version: "2.0.0"
owner_role: qa-lead
accountable_role: qa-lead
created_at: "2026-11-16"
updated_at: "2026-11-16"
source_of_truth:
  is_authoritative: true
  authoritative_source:
    - "tests/contract/test_topic_and_dataset_contracts.py"
    - "tests/data_quality/test_medallion_quality_gates.py"
    - "tests/resilience/test_gap_recovery_and_dlq.py"
    - "tests/e2e/test_data_platform_v01_e2e.py"
related_docs:
  - DP-ROOT-001
  - GOV-STD-QA-001
revision_history:
  - version: "2.0.0"
    date: "2026-11-16"
    author_role: qa-lead
    summary: "Defined Data Plane test strategy separating in-process verified suites from missing live container integration tests."
---

# Data Plane Verification Test Plan

## 1. Verification Scope & Environment Reality `[REQUIRED]`

| Test Suite File | Covered Capabilities | Environment Mode (`AS-IS`) | Known Coverage Gap |
|---|---|---|---|
| `tests/unit/test_domain_and_quant.py` | `CAP-DP-ING-001`, `CAP-DP-LAK-001` | Pure Python + temp SQLite WAL | None for pure math/SQLite store |
| `tests/contract/test_contracts_and_guardrails.py` & `test_topic_and_dataset_contracts.py` | `CAP-DP-STR-001`, `CAP-DP-LAK-001` | In-memory contracts/adapters | Schema compatibility across real Kafka schema registry absent |
| `tests/data_quality/test_medallion_quality_gates.py` | `CAP-DP-LAK-001` | Local temp Parquet & JSON manifests | No MinIO/S3, PySpark, Great Expectations, or ClickHouse dbt live execution |
| `tests/resilience/test_gap_recovery_and_dlq.py` | `CAP-DP-ING-001`, `CAP-DP-STR-001`, `CAP-DP-STR-002` | Embedded ASGI simulator + SQLite + in-memory broker/projector | No live Binance WS disconnect test or live Redis/Kafka container crash test |
| `tests/e2e/test_data_platform_v01_e2e.py` | `CAP-DP-ING-001`, `CAP-DP-STR-001`, `CAP-DP-LAK-001` | Embedded ASGI simulator + local `.local_storage`/`.local_lakehouse` | Zero live Docker container integration (`GAP-QA-001`) |

## 2. Exit Criteria for Marking Live Infrastructure `VERIFIED`

Data Plane capabilities MUST remain `SIMULATED` or `PARTIALLY_IMPLEMENTED` until containerized integration tests execute against live `kafka:9092`, `redis:6379`, `clickhouse:8123`, `postgres:5432`, and `minio:9000`.
