CREATE EXTERNAL TABLE IF NOT EXISTS financials_dwh.dim_date (
  date_key INT,          -- 代理キー (例: YYYYMMDD 形式)
  full_date DATE,        -- 日付 (YYYY-MM-DD 形式)
  year INT,
  month INT,
  day INT,
  day_of_week INT,       -- 曜日 (例: 1=月曜日, 7=日曜日)
  day_name STRING,       -- 曜日名 (例: 'Monday')
  week_of_year INT,
  quarter INT,
  is_weekend BOOLEAN,
  is_holiday BOOLEAN     -- 祝日フラグ (必要に応じて後で更新)
)
STORED AS PARQUET
LOCATION '/data/warehouse/dim/date/';
