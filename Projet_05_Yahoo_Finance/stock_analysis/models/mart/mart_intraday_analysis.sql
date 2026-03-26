-- Mart : analyse intraday pour reporting

SELECT
    date,
    ticker,
    close_price,
    intraday_range,
    intraday_volatility_pct,
    intraday_return_pct

FROM {{ ref('int_stock_intraday_metrics') }}

ORDER BY ticker, date