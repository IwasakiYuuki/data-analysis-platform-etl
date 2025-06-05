import tempfile
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook
import pendulum

from lib.domains.forex.providers.yfinance import YFinanceForexProvider


PROVIDER = "yfinance"
FOREX_PAIRS = [
    "EURUSD=X",
    "JPY=X",
    "GBPUSD=X",
    "AUDUSD=X",
    "NZDUSD=X",
    "EURJPY=X",
    "GBPJPY=X",
    "EURGBP=X",
    "EURCAD=X",
    "EURSEK=X",
    "EURCHF=X",
    "EURHUF=X",
    "CNY=X",
    "HKD=X",
    "SGD=X",
    "INR=X",
    "MXN=X",
    "PHP=X",
    "IDR=X",
    "THB=X",
    "MYR=X",
    "ZAR=X",
    "RUB=X",
][:5]
BASE_PATH = f"/data/lake/forex/{PROVIDER}"

def get_and_upload_forex(
    forex_pairs: list[str],
    start: pendulum.Date,
    end: pendulum.Date,
    webhdfs_conn_id: str = "webhdfs_default",
):
    # Get data
    yp = YFinanceForexProvider()
    forex_data = yp.get_forex_data(
        forex_pairs,
        start,
        end,
        "1m",
    )
    forex_data["year"] = forex_data["datetime"].dt.year
    forex_data["month"] = forex_data["datetime"].dt.month
    forex_data["day"] = forex_data["datetime"].dt.day

    # Upload to HDFS
    for group, gdf in forex_data.groupby(["symbol", "year", "month", "day"]):
        symbol, year, month, day = group  # type: ignore
        hdfs_path = (
            f"{BASE_PATH}"
            f"/symbol={symbol}"
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
    dag_id="lake_yfinance_forex",
    schedule="00 11 * * Mon",
    start_date=datetime(2025, 4, 10),
    catchup=False,
    tags=["DataLake", "YFinance", "Forex"]
) as dag:  
    get_and_upload_forex_task = PythonOperator(
        task_id="get_and_upload_forex_data",
        python_callable=get_and_upload_forex,
        op_kwargs={
            "forex_pairs": FOREX_PAIRS,
            "start": "{{ data_interval_start.start_of('day') }}",
            "end": "{{ data_interval_end.start_of('day') }}",
            "webhdfs_conn_id": "webhdfs_default",
        },
    )
