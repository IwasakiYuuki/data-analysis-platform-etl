import tempfile
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook

from lib.domains.company.providers.yfinance import YFinanceCompanyProvider


PROVIDER = "yfinance"
EXCHANGE = "JPX"
MARKET = "prime"
BASE_INFO_PATH = f"/data/lake/company/info/{PROVIDER}/{EXCHANGE}/{MARKET}"
BASE_FINANCIALS_PATH = f"/data/lake/company/financials/{PROVIDER}/{EXCHANGE}/{MARKET}"
BASE_BALANCE_SHEET_PATH = f"/data/lake/company/balance_sheet/{PROVIDER}/{EXCHANGE}/{MARKET}"
BASE_CASHFLOW_PATH = f"/data/lake/company/cashflow/{PROVIDER}/{EXCHANGE}/{MARKET}"

def get_and_upload_info(
    exchange: str,
    market: str,
    webhdfs_conn_id: str = "webhdfs_default",
):
    # Get data
    yp = YFinanceCompanyProvider()
    tickers = yp.get_tickers(exchange, market)
    info_data = yp.get_company_info_data(tickers=tickers)

    # Upload to HDFS
    for group, gdf in info_data.groupby(["year", "month"]):
        year, month = group  # type: ignore
        hdfs_path = f"{BASE_INFO_PATH}/year={year}/month={month}/data.csv"
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            gdf.to_csv(tmp_file.name, index=False)
            hdfs_hook = WebHDFSHook(webhdfs_conn_id=webhdfs_conn_id)
            hdfs_hook.load_file(tmp_file.name, hdfs_path, overwrite=True)

def get_and_upload_financials(
    exchange: str,
    market: str,
    webhdfs_conn_id: str = "webhdfs_default",
):
    # Get data
    yp = YFinanceCompanyProvider()
    tickers = yp.get_tickers(exchange, market)
    financials_data = yp.get_company_financials_data(
        tickers=tickers,
        period_type="annual"
    )
    financials_data["year"] = financials_data["report_date"].dt.year
    financials_data["month"] = financials_data["report_date"].dt.month

    # Upload to HDFS
    for group, gdf in financials_data.groupby(["year", "month"]):
        year, month = group  # type: ignore
        hdfs_path = f"{BASE_FINANCIALS_PATH}/year={year}/month={month}/data.csv"
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            gdf.to_csv(tmp_file.name, index=False)
            hdfs_hook = WebHDFSHook(webhdfs_conn_id=webhdfs_conn_id)
            hdfs_hook.load_file(tmp_file.name, hdfs_path, overwrite=True)

def get_and_upload_balance_sheet(
    exchange: str,
    market: str,
    webhdfs_conn_id: str = "webhdfs_default",
):
    # Get data
    yp = YFinanceCompanyProvider()
    tickers = yp.get_tickers(exchange, market)
    balance_sheet_data = yp.get_company_balance_sheet_data(
        tickers=tickers,
        period_type="annual"
    )
    balance_sheet_data["year"] = balance_sheet_data["report_date"].dt.year
    balance_sheet_data["month"] = balance_sheet_data["report_date"].dt.month

    # Upload to HDFS
    for group, gdf in balance_sheet_data.groupby(["year", "month"]):
        year, month = group  # type: ignore
        hdfs_path = f"{BASE_BALANCE_SHEET_PATH}/year={year}/month={month}/data.csv"
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            gdf.to_csv(tmp_file.name, index=False)
            hdfs_hook = WebHDFSHook(webhdfs_conn_id=webhdfs_conn_id)
            hdfs_hook.load_file(tmp_file.name, hdfs_path, overwrite=True)

def get_and_upload_cashflow(
    exchange: str,
    market: str,
    webhdfs_conn_id: str = "webhdfs_default",
    ):
    # Get data
    yp = YFinanceCompanyProvider()
    tickers = yp.get_tickers(exchange, market)
    cashflow_data = yp.get_company_cashflow_data(
        tickers=tickers,
        period_type="annual"
    )
    cashflow_data["year"] = cashflow_data["report_date"].dt.year
    cashflow_data["month"] = cashflow_data["report_date"].dt.month

    # Upload to HDFS
    for group, gdf in cashflow_data.groupby(["year", "month"]):
        year, month = group  # type: ignore
        hdfs_path = f"{BASE_CASHFLOW_PATH}/year={year}/month={month}/data.csv"
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            gdf.to_csv(tmp_file.name, index=False)
            hdfs_hook = WebHDFSHook(webhdfs_conn_id=webhdfs_conn_id)
            hdfs_hook.load_file(tmp_file.name, hdfs_path, overwrite=True)

with DAG(
    dag_id="lake_yfinance_company",
    schedule=None,
    start_date=datetime(2025, 4, 10),
    catchup=False,
    tags=["DataLake", "YFinance", "Company"]
) as dag:  
    get_and_upload_info_task = PythonOperator(
        task_id="get_and_upload_info",
        python_callable=get_and_upload_info,
        op_kwargs={
            "exchange": EXCHANGE,
            "market": MARKET,
            "webhdfs_conn_id": "webhdfs_default",
        },
    )

    get_and_upload_financials_task = PythonOperator(
        task_id="get_and_upload_financials",
        python_callable=get_and_upload_financials,
        op_kwargs={
            "exchange": EXCHANGE,
            "market": MARKET,
            "webhdfs_conn_id": "webhdfs_default",
        },
    )

    get_and_upload_balance_sheet_task = PythonOperator(
        task_id="get_and_upload_balance_sheet",
        python_callable=get_and_upload_balance_sheet,
        op_kwargs={
            "exchange": EXCHANGE,
            "market": MARKET,
            "webhdfs_conn_id": "webhdfs_default",
        },
    )

    get_and_upload_cashflow_task = PythonOperator(
        task_id="get_and_upload_cashflow",
        python_callable=get_and_upload_cashflow,
        op_kwargs={
            "exchange": EXCHANGE,
            "market": MARKET,
            "webhdfs_conn_id": "webhdfs_default",
        },
    )

    get_and_upload_info_task >> get_and_upload_financials_task
    get_and_upload_financials_task >> get_and_upload_balance_sheet_task
    get_and_upload_balance_sheet_task >> get_and_upload_cashflow_task
