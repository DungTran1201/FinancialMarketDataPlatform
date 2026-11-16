# Greenfield Engineering Rules

1. **8 GB RAM Budget Discipline**: Design for minimal idle memory, bounded caches, bounded JetStream consumer backpressure, single-writer SQLite WAL (metadata only), and isolated DuckDB/Parquet analytics. Do not introduce Kafka, Redis, ClickHouse, Spark, Flink, Kubernetes, or PostgreSQL without quantified evidence overriding hardware limits.
2. **Persistent Bus vs Ephemeral Cache**: Never treat ordinary in-memory pub/sub as durable delivery; never use SQLite as a high-frequency market tick cache; never run concurrent multi-writer transactions against DuckDB.
3. **Multi-Asset & Multi-Exchange Explicitness**: Binance and OKX connectors must expose independent exchange adapters mapping into canonical `(exchange, market, asset, instrument, symbol, quote_currency, base_currency, contract_type, data_source, exchange_event_time, ingestion_time, event_type)` while archiving raw source payloads.
4. **Quantitative Integrity**: Separate Trade Flow, Order Flow, Liquidity Flow, and Derivatives Positioning. Never equate volume, open interest, or funding rate with net capital inflow. Enforce point-in-time feature joins (`available_at <= decision_time`) and walk-forward cost/slippage deduction before evaluating models against Tier 0 baselines.
5. **No Speculative Implementation or Fake UI**: No mock price arrays or placeholder KPI cards; degraded, stale, unimplemented, or abstained states must be shown explicitly.
6. **Legacy Branch Preservation**: Never delete, force-push, or rewrite `main`, `feat/data-plane-production-delivery`, or other historical branches.

