INSERT INTO TABLE financials_dwh.fact_forex
PARTITION (year, month)
SELECT
  CAST(date_format(to_date(`datetime`), 'yyyyMMdd') AS INT) AS date_key,
  symbol AS currency_id,
  `datetime`,
  open,
  high,
  low,
  close,
  volume,
  year,
  month
FROM
  financials_raw.forex raw
WHERE
  CAST(date_format(to_date(`datetime`), 'yyyyMMdd') AS INT) > COALESCE((SELECT MAX(date_key) FROM financials_dwh.fact_forex), 19700101)
