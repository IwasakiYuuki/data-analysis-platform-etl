CREATE EXTERNAL TABLE IF NOT EXISTS default.raw_company_info (
  symbol STRING,
  shortname STRING,
  longbusinesssummary STRING,
  sector STRING,
  industry STRING,
  fulltimeemployees BIGINT,
  country STRING,
  website STRING,
  marketcap BIGINT,
  currency STRING,
  exchange STRING,
  quotetype STRING,
  market STRING,
  address1 STRING,
  city STRING,
  state STRING,
  zip STRING,
  phone STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar'     = '"',
  'escapeChar'    = '\\',
  'skip.header.line.count'='1'
)
STORED AS TEXTFILE
LOCATION '/data/lake/yfinance/company_info/';
