CREATE OR REPLACE VIEW `crypto_data.v_macd` AS
WITH ema AS (
  SELECT
    date, ticker, close,
    AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS ema_12,
    AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 25 PRECEDING AND CURRENT ROW) AS ema_26
  FROM `crypto_data.prix_crypto`
),
macd AS (
  SELECT
    date, ticker, close,
    ROUND(ema_12 - ema_26, 2) AS macd_line
  FROM ema
)
SELECT
  date, ticker, close, macd_line,
  ROUND(AVG(macd_line) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 8 PRECEDING AND CURRENT ROW), 2) AS signal_line,
  ROUND(macd_line - AVG(macd_line) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 8 PRECEDING AND CURRENT ROW), 2) AS histogram
FROM macd