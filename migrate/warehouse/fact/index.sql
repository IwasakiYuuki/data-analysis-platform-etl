CREATE EXTERNAL TABLE IF NOT EXISTS financials_dwh.fact_index (
  -- Dimensions
  date_key INT,
  index_id STRING,

  `datetime` STRING,
  open DOUBLE,
  high DOUBLE,
  low DOUBLE,
  close DOUBLE,
  volume BIGINT
)
PARTITIONED BY (
  year INT,
  month INT
)
STORED AS PARQUET
LOCATION '/data/warehouse/fact/index/';
