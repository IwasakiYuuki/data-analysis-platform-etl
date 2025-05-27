CREATE EXTERNAL TABLE IF NOT EXISTS default.dim_company (
  company_key BIGINT,        -- 代理キー (symbolのハッシュ値など)
  symbol STRING,             -- 銘柄シンボル (例: '7203.T')
  short_name STRING,         -- 企業名 (短縮)
  long_business_summary STRING, -- 企業概要
  sector STRING,             -- セクター
  industry STRING,           -- 産業
  full_time_employees BIGINT,-- 従業員数
  country STRING,            -- 国
  website STRING,            -- ウェブサイト
  market_cap BIGINT,         -- 時価総額
  currency STRING,           -- 通貨
  exchange STRING,           -- 取引所
  quote_type STRING,         -- 引用タイプ (EQUITYなど)
  market STRING,             -- 市場 (us_marketなど)
  address1 STRING,
  city STRING,
  state STRING,
  zip STRING,
  phone STRING,
  load_timestamp TIMESTAMP   -- ロード日時
)
STORED AS PARQUET
LOCATION '/data/warehouse/dim_company/';
