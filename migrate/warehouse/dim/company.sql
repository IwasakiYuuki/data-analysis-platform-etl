CREATE EXTERNAL TABLE IF NOT EXISTS financials_dwh.dim_company (
  company_id STRING,
  shortname STRING,
  longbusinesssummary STRING,
  sector STRING,
  industry STRING,
  fulltimeemployees INT,
  country STRING,
  website STRING,
  marketcap BIGINT,
  currency STRING,
  quotetype STRING,
  address1 STRING,
  city STRING,
  state STRING,
  zip STRING,
  phone STRING
)
PARTITIONED BY (
  `exchange` STRING,
  market STRING
)
STORED AS PARQUET
LOCATION '/data/warehouse/dim/company/';
