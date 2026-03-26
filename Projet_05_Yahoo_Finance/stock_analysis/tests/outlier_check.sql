-- Test custom : détecte variations > 50%

SELECT
    date,
    ticker,
    daily_return_pct
FROM {{ ref('int_stock_metrics') }}
WHERE ABS(daily_return_pct) > 50