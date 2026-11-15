# Shared Kernel (`src/shared/`)

Contains **only** truly cross-cutting primitives shared across two or more architectural subsystems (`ADR-008`). Must NEVER import from `ingestion`, `streaming`, `lakehouse`, `serving`, or `intelligence`.

## Subpackages

| Directory | Responsibility | File Placement Rules |
|---|---|---|
| `config/` | Runtime environment configuration (`PlatformConfig`) | Strongly-typed config dataclasses; zero service wiring. |
| `contracts/events/` | Canonical `EventEnvelopeV1`, `DeadLetterEnvelopeV1`, topic & event-type enums, deterministic UUIDv5 helpers | Append-only versioned event schemas (`SCHEMA_VERSION_V1`). |
| `contracts/schemas/` | Shared immutable dataset contracts (`CANONICAL_DATASET_CONTRACTS`, `DatasetLayer`, `StorageEngine`) | Natural key and partitioning descriptors across layers. |
| `domain/` | Value objects (`InstrumentKey`, `DecimalPrice`, `BoundedTimeRange`) and pure deterministic quantitative math (`quant.py`) | Standard library / `Decimal` / `math` only; zero I/O or frameworks. |
| `observability/` | Shared OpenMetrics / Prometheus collector (`DataObservabilityMetricsCollector`) | Metric instrumentation definitions shared across planes. |
| `security/` | Shared transport defense primitives (`IPAndEndpointCipher`, `SlidingWindowRateLimiter`, `DomainHttpsEndpointPolicy`, `inspect_request_for_waf_threats`) | Pure crypto/WAF/rate-limit primitives without IAM role/user persistence logic. |

