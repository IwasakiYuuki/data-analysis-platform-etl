CREATE EXTERNAL TABLE IF NOT EXISTS financials_dwh.fact_forex (
  -- Dimensions
  date_key INT,
  currency_id STRING,

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
LOCATION '/data/warehouse/fact/forex/';
