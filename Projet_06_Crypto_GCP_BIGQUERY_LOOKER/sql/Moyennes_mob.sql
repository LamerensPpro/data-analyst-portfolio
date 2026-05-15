CREATE OR REPLACE VIEW `crypto_data.v_moyennes_mobiles` AS
SELECT
  date,
  ticker,
  close,
  ROUND(AVG(close) OVER (
    PARTITION BY ticker ORDER BY date
    ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 2) AS mm_30j,
  ROUND(AVG(close) OVER (
    PARTITION BY ticker ORDER BY date
    ROWS BETWEEN 199 PRECEDING AND CURRENT ROW), 2) AS mm_200j
FROM `crypto_data.prix_crypto`