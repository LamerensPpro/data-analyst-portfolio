-- Staging : nettoyage et typage

SELECT
    CAST("Date" AS DATE) AS date,
    "Ticker" AS ticker,
    CAST("Open" AS NUMERIC(10,2)) AS open_price,
    CAST("High" AS NUMERIC(10,2)) AS high_price,
    CAST("Low" AS NUMERIC(10,2)) AS low_price,
    CAST("Close" AS NUMERIC(10,2)) AS close_price,
    CAST("Volume" AS BIGINT) AS volume

FROM {{ source('stock_data', 'raw_stock_prices') }}

WHERE "Close" IS NOT NULL
  AND "Volume" > 0