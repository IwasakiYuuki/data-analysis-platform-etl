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
    CASE WHEN date_format(d.full_date, 'E') IN ('Sat', 'Sun') THEN true ELSE false END AS is_weekend,
FROM (
  SELECT
    CAST()
      date_add('2000-01-01', n) AS DATE
    ) AS full_date
  FROM
    UNNEST (SEQUENCE(1, 18000)) AS t(n)  -- 大体2000年から2050年まで
) AS d
ORDER BY
  d.full_date
