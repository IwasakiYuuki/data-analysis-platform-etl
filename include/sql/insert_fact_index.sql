INSERT INTO TABLE financials_dwh.fact_index
PARTITION (year, month)
SELECT
  CAST(date_format(to_date(`datetime`), 'yyyyMMdd') AS INT) AS date_key,
  symbol AS index_id,
  `datetime`,
  open,
  high,
  low,
  close,
  volume,
  year,
  month
FROM
  financials_raw.index raw
WHERE
  CAST(date_format(to_date(`datetime`), 'yyyyMMdd') AS INT) > COALESCE((SELECT MAX(date_key) FROM financials_dwh.fact_index), 19700101)

