-- Mart : table finale pour analyse
-- Sélection des métriques clés

SELECT
    date,
    ticker,
    close_price,
    daily_return_pct,
    ma7

FROM {{ ref('int_stock_metrics') }}

ORDER BY ticker, date
