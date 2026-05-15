CREATE OR REPLACE VIEW `crypto_data.v_rsi` AS
WITH daily_changes AS (
  SELECT
    date, ticker, close,
    close - LAG(close) OVER (PARTITION BY ticker ORDER BY date) AS change
  FROM `crypto_data.prix_crypto`
),
gains_losses AS (
  SELECT
    date, ticker, close,
    GREATEST(change, 0) AS gain,
    ABS(LEAST(change, 0)) AS loss
  FROM daily_changes
),
avg_gl AS (
  SELECT
    date, ticker, close,
    AVG(gain) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS avg_gain,
    AVG(loss) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS avg_loss
  FROM gains_losses
)
SELECT
  date, ticker, close,
  ROUND(100 - (100 / (1 + avg_gain / NULLIF(avg_loss, 0))), 2) AS rsi_14
FROM avg_gl