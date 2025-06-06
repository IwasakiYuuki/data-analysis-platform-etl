CREATE EXTERNAL TABLE IF NOT EXISTS financials_raw.forex (
  `datetime` STRING,
  open DOUBLE,
  high DOUBLE,
  low DOUBLE,
  close DOUBLE,
  volume BIGINT,
)
PARTITIONED BY (
  provider STRING,
  symbol STRING,
  year STRING,
  month STRING,
  day STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde' -- CSV用のSerDeを使用
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar'     = '"',
  'escapeChar'    = '\\',
  'skip.header.line.count'='1' -- ヘッダー行をスキップする設定
)
STORED AS TEXTFILE
LOCATION '/data/lake/forex/';
