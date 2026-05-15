CREATE OR REPLACE VIEW `crypto_data.v_variation_journaliere` AS
SELECT
  date,
  ticker,
  close,
  LAG(close) OVER (PARTITION BY ticker ORDER BY date) AS close_veille,
  ROUND((close - LAG(close) OVER (PARTITION BY ticker ORDER BY date)) 
    / LAG(close) OVER (PARTITION BY ticker ORDER BY date) * 100, 2) AS variation_pct
FROM `crypto_data.prix_crypto`