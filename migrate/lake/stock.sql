CREATE EXTERNAL TABLE IF NOT EXISTS financials_raw.stock (
  `datetime` STRING,
  open DOUBLE,
  high DOUBLE,
  low DOUBLE,
  close DOUBLE,
  volume BIGINT,
  symbol STRING,
)
PARTITIONED BY (
  provider STRING,
  exchange STRING,
  market STRING,
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
LOCATION '/data/lake/stock/';
