# Diagram 01: System Context Diagram (C4 Level 1)

## Architectural Explanation

The **System Context Diagram** establishes the boundary of the **Real-time Financial Market Data Platform** and its interactions with external actors and systems:

1. **External Data Providers (Upstream)**:
   - **Binance WebSocket API**: Pushes real-time market events (trades, klines, 24h tickers, order book depth) over persistent TLS WebSocket connections.
   - **Binance REST API**: Serves paginated historical klines, aggregated trades, order book snapshots, and exchange instrument metadata over HTTPS.
   - **Future Exchange Providers**: Extensible via the Collector Provider Port without altering core platform internals.
2. **External AI Infrastructure**:
   - **LLM Provider API**: Invoked asynchronously and exclusively by the Intelligence Plane for narrative synthesis and tool planning. Never sits on the critical path of data ingestion or market data serving.
3. **Human & Programmatic Consumers (Downstream)**:
   - **Market Analysts & Traders**: Query real-time prices, historical charts, quantitative analytics, and trigger AI market investigations via REST, WebSocket, and SSE APIs, or explore BI dashboards in Apache Superset.
   - **External Client Applications**: Consume versioned REST (`/api/v1/*`) and WebSocket (`/ws/v1/market/stream`) feeds.
   - **Platform Operators & Data Engineers**: Manage monitored symbols, inspect data quality and consumer lag in Grafana, and orchestrate backfills via Apache Airflow.

```mermaid
flowchart TB
    subgraph Actors["External Users & Client Systems"]
        Trader["Market Analyst / Trader"]
        ClientApp["External Trading / Analytics App"]
        Operator["Platform Operator / Data Engineer"]
    end

    subgraph Providers["External Financial Data Providers"]
        BinanceWS["Binance WebSocket API<br/>(Real-time Trades, Klines, Tickers, Depth)"]
        BinanceREST["Binance REST API<br/>(Historical Klines, Trades, Exchange Info)"]
        FutureEx["Future Financial Providers<br/>(Coinbase, Kraken, Equities)"]
    end

    subgraph ExternalAI["External AI Providers (Optional / Isolated)"]
        LLMAPI["LLM Provider API<br/>(OpenAI / Anthropic / Gemini / Local)"]
    end

    subgraph PlatformBoundary["Real-time Financial Market Data Platform"]
        DataPlane["Data Plane<br/>(Ingestion, Kafka, Redis, ClickHouse, Lakehouse)"]
        AppPlane["Application & Control Plane<br/>(FastAPI Backend, Auth/RBAC, PostgreSQL, Superset)"]
        IntelPlane["Intelligence Plane<br/>(LangGraph Agent Service, Tool Gateway)"]
        ObsPlane["Observability & Governance<br/>(Prometheus, Grafana, Great Expectations)"]
    end

    BinanceWS -->|"WSS (TLS 1.3) JSON Streams"| DataPlane
    BinanceREST -->|"HTTPS REST Polling & Backfill"| DataPlane
    FutureEx -.->|"Normalized Provider Adapter"| DataPlane

    DataPlane -->|"Hot State (Redis) & OLAP (ClickHouse)"| AppPlane
    DataPlane -->|"Threshold Anomaly Events"| IntelPlane
    IntelPlane -->|"Read-Only Deterministic Tool Calls"| DataPlane
    IntelPlane -->|"HTTPS (Circuit-Protected)"| LLMAPI

    Trader -->|"HTTPS REST / WSS / SSE / Superset UI"| AppPlane
    ClientApp -->|"HTTPS REST & WSS API (/api/v1, /ws/v1)"| AppPlane
    AppPlane -->|"Async Job Enqueue & State Read"| IntelPlane
    Operator -->|"Admin API / Airflow UI / Grafana UI"| AppPlane
    Operator -->|"Metrics & Alerts Inspection"| ObsPlane
```

