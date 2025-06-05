import tempfile
import pendulum
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook

from lib.domains.stock.providers.yfinance import YFinanceStockProvider


PROVIDER = "yfinance"
EXCHANGE = "JPX"
MARKET = "prime"
BASE_PATH = f"/data/lake/stock/{PROVIDER}/{EXCHANGE}/{MARKET}"

def get_and_upload_stock(
    exchange: str,
    market: str,
    start: pendulum.Date,
    end: pendulum.Date,
    webhdfs_conn_id: str = "webhdfs_default",
):
    # Get data
    yp = YFinanceStockProvider()
    stock_data = yp.get_stock_data_by_market(
        exchange,
        market,
        start,
        end,
        "1m",
    )
    stock_data["year"] = stock_data["datetime"].dt.year
    stock_data["month"] = stock_data["datetime"].dt.month
    stock_data["day"] = stock_data["datetime"].dt.day

    # Upload to HDFS
    for group, gdf in stock_data.groupby(["year", "month", "day"]):
        year, month, day = group  # type: ignore
        hdfs_path = (
            f"{BASE_PATH}"
            f"/year={year}"
            f"/month={month}"
            f"/day={day}"
            "/data.csv"
        )
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            gdf.to_csv(tmp_file.name, index=False)
            hdfs_hook = WebHDFSHook(webhdfs_conn_id=webhdfs_conn_id)
            hdfs_hook.load_file(tmp_file.name, hdfs_path, overwrite=True)


with DAG(
    dag_id="lake_yfinance_stock",
    schedule="00 11 * * Mon",
    start_date=datetime(2025, 4, 10),
    catchup=False,
    tags=["DataLake", "YFinance", "Stock"]
) as dag:  
    get_and_upload_stock_task = PythonOperator(
        task_id="get_and_upload_stock_data",
        python_callable=get_and_upload_stock,
        op_kwargs={
            "exchange": EXCHANGE,
            "market": MARKET,
            "start": "{{ data_interval_start.date().subtract(days=2) }}",
            "end": "{{ data_interval_end.date().subtract(days=2) }}",
            "webhdfs_conn_id": "webhdfs_default",
        },
    )
