CREATE OR REPLACE VIEW `crypto_data.v_volatilite` AS
SELECT
  date,
  ticker,
  ROUND(STDDEV(close) OVER (
    PARTITION BY ticker ORDER BY date
    ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 2) AS volatilite_30j
FROM `crypto_data.prix_crypto`