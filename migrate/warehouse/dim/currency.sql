CREATE EXTERNAL TABLE IF NOT EXISTS financials_dwh.dim_currency (
  currency_id STRING,
)
STORED AS PARQUET
LOCATION '/data/warehouse/dim/currency/';
