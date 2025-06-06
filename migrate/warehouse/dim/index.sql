CREATE EXTERNAL TABLE IF NOT EXISTS financials_dwh.dim_index (
  index_id STRING,
)
STORED AS PARQUET
LOCATION '/data/warehouse/dim/index/';
