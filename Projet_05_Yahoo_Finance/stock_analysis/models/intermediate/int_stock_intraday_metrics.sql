-- Intermediate : métriques intraday

SELECT
    date,
    ticker,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    (high_price - low_price) AS intraday_range,
    
    ((high_price - low_price) / NULLIF(open_price, 0) * 100) AS intraday_volatility_pct,
    
    ((close_price - open_price) / NULLIF(open_price, 0) * 100) AS intraday_return_pct


FROM {{ ref('stg_stock_prices') }}
