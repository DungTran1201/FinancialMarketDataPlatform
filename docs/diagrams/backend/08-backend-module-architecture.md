# Diagram 08: Backend Module & Clean/Hexagonal Architecture

## Architectural Explanation

The **Backend Module Architecture** demonstrates how the FastAPI Modular Monolith (`backend-api`) is organized into eight cohesive business domain modules (`market`, `historical`, `analytics`, `catalog`, `iam`, `platform_config`, `agent_api`, `reporting`) and how each module internally adheres to **Clean / Hexagonal Architecture**:
- **Presentation Layer**: FastAPI Routers, HTTP Request/Response Pydantic schemas, Authentication & Rate-Limit dependencies.
- **Application Layer**: Use Cases, Query Handlers, Command Handlers, and DTOs.
- **Domain Layer (Core)**: Pure Python Entities, Value Objects (`Symbol`, `Price`, `TimeRange`), Domain Services, and Repository/Adapter Port Interfaces (`Protocol`). Has **zero outward dependencies**.
- **Infrastructure Layer**: Concrete Adapters implementing Domain Ports (`RedisMarketHotAdapter`, `ClickHouseHistoricalAdapter`, `PostgresControlAdapter`, `KafkaEventPublisher`).

```mermaid
flowchart TB
    subgraph FastAPIMonolith["FastAPI Modular Monolith (src/backend/)"]
        subgraph DomainModules["Business Domain Modules"]
            M1["market"]
            M2["historical"]
            M3["analytics"]
            M4["catalog"]
            M5["iam"]
            M6["platform_config"]
            M7["agent_api"]
            M8["reporting"]
        end

        subgraph HexagonalZoom["Clean / Hexagonal Layering (Inside Each Domain Module)"]
            direction TB
            Pres["Presentation Layer<br/>(FastAPI Routers, HTTP Schemas, Auth Dependencies)"]
            App["Application Layer<br/>(Query Handlers, Command Handlers, Use Cases)"]
            Dom["Domain Layer (Pure Core)<br/>(Entities, Value Objects, Business Rules, Port Protocols)"]
            Infra["Infrastructure Layer (Adapters)<br/>(RedisAdapter, ClickHouseRepository, PostgresRepository)"]

            Pres -->|"Calls"| App
            App -->|"Orchestrates"| Dom
            Infra -->|"Implements Ports Defined In"| Dom
        end
    end

    subgraph ExternalDrivers["External Infrastructure & Databases"]
        Redis[("Redis 7")]
        ClickHouse[("ClickHouse")]
        Postgres[("PostgreSQL 16")]
        Kafka[("Apache Kafka")]
    end

    Infra --> Redis
    Infra --> ClickHouse
    Infra --> Postgres
    Infra --> Kafka
```

