INSERT OVERWRITE TABLE default.dim_company
SELECT
    hash(rc.symbol) AS company_key,
    rc.symbol,
    rc.shortname,
    rc.longbusinesssummary,
    rc.sector,
    rc.industry,
    rc.fulltimeemployees,
    rc.country,
    rc.website,
    rc.marketcap,
    rc.currency,
    rc.exchange,
    rc.quotetype,
    rc.market,
    rc.address1,
    rc.city,
    rc.state,
    rc.zip,
    rc.phone,
    current_timestamp() AS load_timestamp
FROM
    default.raw_company_info rc;
