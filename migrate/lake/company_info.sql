CREATE EXTERNAL TABLE IF NOT EXISTS financials_raw.company_info (
  symbol STRING,
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
  provider STRING,
  `exchange` STRING,
  market STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar'     = '"',
  'escapeChar'    = '\\',
  'skip.header.line.count'='1'
)
STORED AS TEXTFILE
LOCATION '/data/lake/company/info/';
