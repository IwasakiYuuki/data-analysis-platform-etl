INSERT INTO financials_dwh.dim_date
SELECT
  CAST(date_format(d.full_date, 'yyyyMMdd') AS INT) AS date_key,
  d.full_date AS full_date,
  year(d.full_date) AS year,
  month(d.full_date) AS month,
  day(d.full_date) AS day,
  CASE date_format(d.full_date, 'E')
      WHEN 'Mon' THEN 1 WHEN 'Tue' THEN 2 WHEN 'Wed' THEN 3
      WHEN 'Thu' THEN 4 WHEN 'Fri' THEN 5 WHEN 'Sat' THEN 6
      WHEN 'Sun' THEN 7 ELSE NULL
  END AS day_of_week,
  date_format(d.full_date, 'EEEE') AS day_name, -- 例: Monday
  weekofyear(d.full_date) AS week_of_year,
  quarter(d.full_date) AS quarter,
  CASE WHEN date_format(d.full_date, 'E') IN ('Sat', 'Sun') THEN true ELSE false END AS is_weekend
FROM (
  SELECT DISTINCT to_date(`datetime`) AS full_date
  FROM financials_raw.stock
  UNION
  SELECT DISTINCT to_date(`datetime`) AS full_date
  FROM financials_raw.forex
  UNION
  SELECT DISTINCT to_date(`datetime`) AS full_date
  FROM financials_raw.index
  UNION
  SELECT DISTINCT to_date(report_date) AS full_date
  FROM financials_raw.company_financials
  UNION
  SELECT DISTINCT to_date(report_date) AS full_date
  FROM financials_raw.company_balance_sheet
  UNION
  SELECT DISTINCT to_date(report_date) AS full_date
  FROM financials_raw.company_cashflow
) AS d
LEFT JOIN financials_dwh.dim_date existing ON CAST(date_format(d.full_date, 'yyyyMMdd') AS INT) = existing.date_key
WHERE existing.date_key IS NULL
  AND d.full_date IS NOT NULL
ORDER BY
  d.full_date
