# Diagram 16: Security & Trust Boundary Diagram

## Architectural Explanation

The **Security & Trust Boundary Diagram** defines the five concentric trust zones across the platform and the mandatory controls enforced at every boundary crossing:
1. **Zone 1 — Untrusted External Internet**: Public API clients, browsers, external exchange endpoints (Binance), and third-party LLM APIs.
2. **Zone 2 — Edge & API Gateway Boundary (`frontend_net`)**: FastAPI enforces JWT/API-Key authentication, RBAC role checks, sliding-window rate limits, request payload validation, and query cost limits before any internal service is reached.
3. **Zone 3 — Application & Control Zone (`app_control_net`)**: Holds PostgreSQL (accessed via `app_rw` credentials) and operational management services.
4. **Zone 4 — Isolated Intelligence Sandbox (`intel_sandbox_net`)**: Runs the LangGraph `agent-worker`. Has **no write credentials** to any market database; connects to ClickHouse exclusively via `agent_ro` (`readonly=1`) and Redis read-only commands through the Controlled Tool Gateway.
5. **Zone 5 — Core Data Plane Zone (`data_plane_net`)**: Houses Kafka, Redis, ClickHouse, and MinIO. No external client can route directly to Zone 5 containers.

```mermaid
flowchart TB
    subgraph Zone1["Trust Zone 1: External & Untrusted Networks"]
        ExtClient["External Clients / Browsers"]
        BinanceAPI["Binance Exchange APIs (WSS / HTTPS)"]
        ExtLLM["External LLM Provider API"]
    end

    subgraph Zone2["Trust Zone 2: API Edge & Access Control Boundary"]
        AuthGate["FastAPI Security Gate<br/>(JWT/API-Key Auth, RBAC, Rate Limiting, Input & Range Bounds)"]
    end

    subgraph Zone3["Trust Zone 3: Control Plane Zone (Least-Privilege OLTP)"]
        PGControl[("PostgreSQL 16<br/>Roles: postgres_admin, app_rw, agent_rw, airflow_rw")]
        SecretStore["Environment / Secret Mounts<br/>(Zero Hardcoded Credentials)"]
    end

    subgraph Zone4["Trust Zone 4: Intelligence Sandbox (Read-Only Data Access)"]
        LangGraph["LangGraph Agent Worker<br/>(Token Cap, Max 6 Iterations, 90s Timeout)"]
        ToolFirewall["Controlled Tool Gateway<br/>(10 Whitelisted Tools, 5s Timeout, Row Caps)"]
    end

    subgraph Zone5["Trust Zone 5: Core Data Plane (Internal High-Throughput Storage)"]
        Collectors["Ingestion Collectors<br/>(Outbound TLS Only + Schema Validation)"]
        KafkaInternal[("Apache Kafka<br/>(Producer/Consumer ACLs)")]
        RedisInternal[("Redis 7<br/>(Requirepass + Prefix Isolation)")]
        CHInternal[("ClickHouse OLAP<br/>Roles: ingestion_writer, api_reader, agent_ro [readonly=1]")]
        MinIOInternal[("MinIO Lakehouse<br/>(Scoped Bucket IAM Policies: bronze-writer, spark-rw)")]
    end

    ExtClient -->|"HTTPS / WSS"| AuthGate
    AuthGate -->|"Authorized app_rw"| PGControl
    AuthGate -->|"Authorized api_reader"| RedisInternal & CHInternal
    AuthGate -->|"Async Job Enqueue"| LangGraph

    Collectors -->|"Outbound TLS 1.3 Only"| BinanceAPI
    Collectors -->|"Validated Canonical Events"| KafkaInternal
    KafkaInternal -->|"ingestion_writer"| RedisInternal & CHInternal & MinIOInternal

    LangGraph -->|"Outbound HTTPS (API Key Scoped)"| ExtLLM
    LangGraph -->|"Checkpoint & Audit Only (agent_rw)"| PGControl
    LangGraph -->|"Tool Calls Only"| ToolFirewall
    ToolFirewall -->|"Read-Only (agent_ro, readonly=1)"| RedisInternal & CHInternal
```

