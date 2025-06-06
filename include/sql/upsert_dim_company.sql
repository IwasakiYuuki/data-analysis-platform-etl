INSERT INTO financials_dwh.dim_company
SELECT
  DISTINCT
  d.symbol AS company_id,
  d.shortname,
  d.longbusinesssummary,
  d.sector,
  d.industry,
  d.fulltimeemployees,
  d.country,
  d.website,
  d.marketcap,
  d.currency,
  d.quotetype,
  d.address1,
  d.city,
  d.state,
  d.zip,
  d.phone,
  d.`exchange`,
  d.market
FROM 
  financials_raw.company_info AS d
LEFT JOIN financials_dwh.dim_company existing ON d.symbol = existing.company_id
WHERE existing.company_id IS NULL
  AND d.symbol IS NOT NULL
