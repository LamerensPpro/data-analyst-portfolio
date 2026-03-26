-- Intermediate : calculs techniques
-- Variation journalière et moyenne mobile 7 jours

SELECT
    date,
    ticker,
    close_price,
    
    -- Variation journalière en %
    (close_price / NULLIF(LAG(close_price) OVER (PARTITION BY ticker ORDER BY date), 0) - 1) * 100 
        AS daily_return_pct,
    
    -- Moyenne mobile 7 jours
    AVG(close_price) OVER (
        PARTITION BY ticker 
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS ma7

FROM {{ ref('stg_stock_prices') }}