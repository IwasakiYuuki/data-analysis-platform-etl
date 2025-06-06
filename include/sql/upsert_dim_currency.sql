INSERT INTO financials_dwh.dim_currency
SELECT
  DISTINCT
  symbol AS currency_id
FROM 
  financials_raw.forex AS d
LEFT JOIN financials_dwh.dim_currency existing ON d.symbol = existing.currency_id
WHERE existing.currency_id IS NULL
  AND d.symbol IS NOT NULL
