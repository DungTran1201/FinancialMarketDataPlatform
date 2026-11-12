# ADR-001: Overall Three-Plane Architecture & Streaming-First Hybrid Lakehouse

- **Status**: Accepted
- **Date**: 2026-11-12
- **Deciders**: System Architecture & Data Platform Architecture Team

---

## 1. Decision Title

Adopt a **Three-Plane Event-Driven Data Platform with a Streaming-First Hybrid Lakehouse Architecture**, strictly isolating the **Data Plane**, **Application & Control Plane**, and **Intelligence Plane**.

---

## 2. Context

The Real-time Financial Market Data Platform must simultaneously support:
1. Sub-second ingestion and distribution of high-frequency exchange events (trades, klines, tickers, order book depth) from Binance and future providers.
2. Low-latency hot queries (latest price, real-time snapshots) alongside heavy analytical time-series queries and historical Lakehouse backfills.
3. Application control, user authentication, RBAC, and operational metadata management.
4. AI Agent workflows (LangGraph) for market intelligence, quantitative analysis, and anomaly investigation.
5. Local development and single-host/resource-constrained deployment via Docker Compose without requiring Kubernetes.

---

## 3. Problem Statement

How do we structure the overall system so that high-throughput market data ingestion, low-latency API serving, batch analytical processing, and non-deterministic/slow LLM Agent workflows coexist without resource contention, cascading failures, or tight coupling?

---

## 4. Selected Option

Divide the platform into three strictly bounded architectural planes with explicit communication contracts and unidirectional failure isolation:

1. **Data Plane**:
   - Owns real-time and historical ingestion (Python Collectors), event streaming (Apache Kafka), hot state projection (Redis), real-time/historical OLAP (ClickHouse), Lakehouse storage (MinIO + Parquet + Apache Iceberg), batch processing (PySpark + dbt Core), data quality (Great Expectations), and batch orchestration (Apache Airflow).
2. **Application & Control Plane**:
   - Owns external REST/WebSocket APIs (FastAPI Modular Monolith), authentication/RBAC, user/configuration metadata, ingestion watermarks, and task orchestration state (PostgreSQL).
3. **Intelligence Plane**:
   - Owns stateful AI Agent workflows (LangGraph), LLM Provider Adapters, deterministic Tool Gateway, quantitative calculation tools, and agent run persistence/observability.

### Critical Isolation Rule
- The **Data Plane** has **zero runtime dependency** on the Intelligence Plane. If all LLM providers or Agent workers fail, market data collection, streaming, storage, and API serving continue at 100% capacity.

---

## 5. Alternative Options Considered

### Alternative A: Monolithic Single-Database Architecture (FastAPI + PostgreSQL/TimescaleDB Only)
- **Description**: Route all ingestion, historical storage, control metadata, and agent queries through a single relational/time-series database and a single backend process.
- **Rejection Reason**: High-frequency tick writes and analytical scans compete directly with transactional queries and API latency; lacks raw immutable Lakehouse storage for schema evolution and large-scale replay.

### Alternative B: Fully Distributed Microservices Architecture (10+ Independent Services + Kubernetes)
- **Description**: Deploy separate microservices for Market, Historical, Analytics, Catalog, Auth, Notification, and multiple specialized Agents over Kubernetes.
- **Rejection Reason**: Violates Objective O7 (Resource Efficiency) and Section 9.1 (Microservices Limitations). Introduces severe operational overhead, network serialization latency, distributed tracing complexity, and excessive memory footprint for a local/constrained deployment.

### Alternative C: Pure Batch Lakehouse Only (REST Collectors $\rightarrow$ MinIO/Iceberg $\rightarrow$ Spark/Trino)
- **Description**: Store all data in Parquet/Iceberg and serve all queries via Spark or Trino.
- **Rejection Reason**: Violates Objective O1 and O2. Object storage and batch engines cannot deliver sub-50ms hot price queries or sub-second WebSocket streaming updates.

---

## 6. Decision Rationale

Separating the platform into three planes aligns physical and logical boundaries with workload characteristics:
- **Throughput vs. Latency**: Event streaming (Kafka) decouples producers from heterogeneous consumers (Redis for sub-second state, ClickHouse for sub-second OLAP, MinIO/Iceberg for durable cost-effective history).
- **Determinism vs. Probabilistic AI**: Keeping LangGraph inside an isolated Intelligence Plane ensures LLM latency spikes, rate limits, or hallucinations never impact financial data ingestion or deterministic API endpoints.

---

## 7. Benefits

- **Fault Isolation**: Failure in the Intelligence Plane, Lakehouse batch jobs, or BI layer does not halt real-time market ingestion or hot data serving.
- **Independent Scaling**: Collectors, Kafka consumers, FastAPI workers, Spark batch jobs, and Agent workers can be scaled or paused independently via Docker Compose profiles.
- **Provider Agnosticism**: External exchange specifics are terminated at the Collector boundary and normalized into canonical Kafka event contracts.

---

## 8. Drawbacks

- **Multi-Engine Operational Footprint**: Operating Kafka, Redis, ClickHouse, PostgreSQL, and MinIO requires clear Docker Compose resource limits and profile management on developer machines.
- **Eventual Consistency Across Planes**: Data written to Kafka reaches Redis, ClickHouse, and Iceberg at different latencies ($<500\text{ ms}$, $1-5\text{ s}$, and $5-15\text{ m}$ respectively).

---

## 9. Architectural Limitations

- Does **not** provide cross-engine distributed ACID transactions (e.g., no two-phase commit across Redis, ClickHouse, and MinIO).
- Does **not** provide sub-millisecond co-located high-frequency trading (HFT) execution capabilities; this is a market data analytics and intelligence platform, not an order execution engine.

---

## 10. Operational Implications

- Services are grouped into Docker Compose profiles (`core`, `lakehouse`, `observability`, `intelligence`, `bi`) so engineers can run the essential real-time path (`core`) with minimal memory ($<6\text{ GB}$ RAM) and activate heavy batch/BI components on demand.
- Health checks and Prometheus metrics must monitor inter-plane boundaries (Kafka consumer lag, Redis freshness, ClickHouse insert batch latency, Agent queue depth).

---

## 11. Consequences

- Every data flow between planes must use explicit contracts (Kafka schemas, typed Repository ports, or versioned Tool Gateway interfaces).
- Direct database sharing across planes is restricted to read-only projections with dedicated least-privilege database roles.

---

## 12. Conditions That Could Invalidate This Decision

1. If deployment constraints shrink to an ultra-lightweight edge device ($<2\text{ GB}$ RAM total), operating Kafka + ClickHouse + PostgreSQL + MinIO becomes infeasible and would require consolidating onto a single embedded analytical engine (e.g., DuckDB + SQLite).
2. If organizational structure grows to multiple autonomous engineering teams owning separate bounded contexts with independent release cadences, specific modules within the FastAPI Modular Monolith may be extracted into standalone services.

