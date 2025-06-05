import tempfile
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook
import pendulum

from lib.domains.index.providers.yfinance import YFinanceIndexProvider


PROVIDER = "yfinance"
INDEX_SYMBOLS = [
    "^GSPC",  # S&P500
    "^DJI",   # NYダウ
    "^IXIC", # NASDAQ
    "^NYA", # NYSE総合
    "^XAX", # AMEX総合
    "^BUK1000", # ブルームバーグ米国株式
    "^RUT", # ラッセル2000
    "^VIX", # VIX指数
    "^FTSE", # FTSE100
    "^GDAXI", # DAX
    "^FCHI", # CAC40
    "^STOXX50E", # EURO STOXX 50
    "^N100", # EURO STOXX 100
    "^BFX", # BEL 20
    "MOEX.ME", # MOEX
    "^HSI", # HSI
    "^STI", # STI
    "^AXJO", # ASX 200
    "^AORD", # S&P/ASX 200
    "^BSESN", # BSE SENSEX
    "^JKSE", # IDX Composite
    "^KLSE", # FTSE Bursa Malaysia KLCI
    "^NZ50", # S&P/NZX 50 Index
    "^KS11", # KOSPI Composite Index
    "^TWII", # TSEC Capitalization Weighted Stock Index
    "^GSPTSE", # TSEC Taiwan Weighted Index
    "^BVSP", # Bovespa Index
    "^MXX", # IPC Mexico
    "^IPSA", # IPC Mexico
    "^MERV", # MERVAL
    "^TA125.TA", # TA-125 Index
    "^CASE30", # EGX 30 Prise Return Index
    "^JNOU.JO", # Top 40 USD Net Total Return Index
    "DX-Y.NYB", # US Dollar Index
    "^125904-USD-STRD", # MSCI EUROPE
    "^XDB", # British Pound Currency Index
    "^XDE", # Euro Currency Index
    "000001.SS", # SSE Composite Index
    "^N225", # Nikkei 225
    "^XDN", # Japanese Yen Currency Index
    "^XDA", # Australian Dollar Currency Index
]
BASE_PATH = f"/data/lake/index/{PROVIDER}"

def get_and_upload_index(
    index_symbols: list[str],
    start: pendulum.Date,
    end: pendulum.Date,
    webhdfs_conn_id: str = "webhdfs_default",
):
    # Get data
    yp = YFinanceIndexProvider()
    index_data = yp.get_index_data(
        index_symbols,
        start,
        end,
        "1m",
    )
    index_data["year"] = index_data["datetime"].dt.year
    index_data["month"] = index_data["datetime"].dt.month
    index_data["day"] = index_data["datetime"].dt.day

    # Upload to HDFS
    for group, gdf in index_data.groupby(["symbol", "year", "month", "day"]):
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
    dag_id="lake_yfinance_index",
    schedule="00 11 * * Mon",
    start_date=datetime(2025, 4, 10),
    catchup=False,
    tags=["DataLake", "YFinance", "Index"]
) as dag:  
    get_and_upload_index_task = PythonOperator(
        task_id="get_and_upload_index_data",
        python_callable=get_and_upload_index,
        op_kwargs={
            "index_symbols": INDEX_SYMBOLS,
            "start": "{{ data_interval_start.date().substact(days=2) }}",
            "end": "{{ data_interval_end.date().substact(days=2) }}",
            "webhdfs_conn_id": "webhdfs_default",
        },
    )
