-- Gold Mart: Daily OHLCV & Volume Summary per Instrument (ADR-002 / ADR-003)
{{
    config(
        materialized='incremental',
        engine='ReplacingMergeTree()',
        order_by='(provider, symbol, trading_day)',
        unique_key=['provider', 'symbol', 'trading_day']
    )
}}

SELECT
    provider,
    symbol,
    toDate(open_time) AS trading_day,
    argMin(open_price, open_time) AS daily_open_price,
    max(high_price) AS daily_high_price,
    min(low_price) AS daily_low_price,
    argMax(close_price, open_time) AS daily_close_price,
    sum(base_volume) AS daily_base_volume,
    sum(quote_volume) AS daily_quote_volume,
    sum(trade_count) AS daily_trade_count,
    max(exchange_event_time) AS last_event_time,
    now64(3, 'UTC') AS dbt_updated_at
FROM market_data.market_klines
WHERE is_closed = true
{% if is_incremental() %}
  AND toDate(open_time) >= (SELECT max(trading_day) FROM {{ this }})
{% endif %}
GROUP BY
    provider,
    symbol,
    toDate(open_time)

