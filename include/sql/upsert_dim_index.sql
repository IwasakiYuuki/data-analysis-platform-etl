INSERT INTO financials_dwh.dim_index
SELECT
  DISTINCT
  symbol AS index_id
FROM 
  financials_raw.index AS d
LEFT JOIN financials_dwh.dim_index existing ON d.symbol = existing.index_id
WHERE existing.index_id IS NULL
  AND d.symbol IS NOT NULL
