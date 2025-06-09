INSERT INTO TABLE financials_dwh.fact_stock
PARTITION (year, month)
SELECT
  CAST(date_format(to_date(`datetime`), 'yyyyMMdd') AS INT) AS date_key,
  symbol AS company_id,
  `datetime`,
  open,
  high,
  low,
  close,
  volume,
  year,
  month
FROM
  financials_raw.stock raw
WHERE
  CAST(date_format(to_date(`datetime`), 'yyyyMMdd') AS INT) > COALESCE((SELECT MAX(date_key) FROM financials_dwh.fact_stock), 19700101)

