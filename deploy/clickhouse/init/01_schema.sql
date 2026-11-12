-- =============================================================================
-- ClickHouse Real-Time & Historical OLAP Schema Initialization
-- Designed for partition-pruned time-series queries & ReplacingMergeTree dedup.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS market_data;

CREATE TABLE IF NOT EXISTS market_data.market_trades
(
    provider             LowCardinality(String),
    symbol               LowCardinality(String),
    trade_id             UInt64,
    price                Decimal128(18),
    quantity             Decimal128(18),
    quote_volume         Decimal128(18),
    buyer_order_id       UInt64,
    seller_order_id      UInt64,
    is_buyer_maker       Bool,
    trade_time           DateTime64(3, 'UTC'),
    exchange_event_time  DateTime64(3, 'UTC'),
    ingested_at          DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(ingested_at)
PARTITION BY toYYYYMM(trade_time)
ORDER BY (provider, symbol, trade_time, trade_id)
TTL toDateTime(trade_time) + INTERVAL 90 DAY DELETE
SETTINGS index_granularity = 8192;

CREATE TABLE IF NOT EXISTS market_data.market_klines
(
    provider                LowCardinality(String),
    symbol                  LowCardinality(String),
    interval                LowCardinality(String),
    open_time               DateTime64(3, 'UTC'),
    close_time              DateTime64(3, 'UTC'),
    open_price              Decimal128(18),
    high_price              Decimal128(18),
    low_price               Decimal128(18),
    close_price             Decimal128(18),
    base_volume             Decimal128(18),
    quote_volume            Decimal128(18),
    trade_count             UInt64,
    taker_buy_base_volume   Decimal128(18),
    taker_buy_quote_volume  Decimal128(18),
    is_closed               Bool,
    exchange_event_time     DateTime64(3, 'UTC'),
    ingested_at             DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(exchange_event_time)
PARTITION BY toYYYYMM(open_time)
ORDER BY (provider, symbol, interval, open_time)
SETTINGS index_granularity = 8192;

CREATE TABLE IF NOT EXISTS market_data.market_tickers
(
    provider                LowCardinality(String),
    symbol                  LowCardinality(String),
    last_price              Decimal128(18),
    best_bid_price          Decimal128(18),
    best_bid_qty            Decimal128(18),
    best_ask_price          Decimal128(18),
    best_ask_qty            Decimal128(18),
    price_change_24h        Decimal128(18),
    price_change_pct_24h    Decimal64(6),
    vwap_24h                Decimal128(18),
    high_24h                Decimal128(18),
    low_24h                 Decimal128(18),
    base_volume_24h         Decimal128(18),
    quote_volume_24h        Decimal128(18),
    trade_count_24h         UInt64,
    exchange_event_time     DateTime64(3, 'UTC'),
    ingested_at             DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(exchange_event_time)
PARTITION BY toYYYYMM(exchange_event_time)
ORDER BY (provider, symbol, exchange_event_time)
TTL toDateTime(exchange_event_time) + INTERVAL 90 DAY DELETE
SETTINGS index_granularity = 8192;

