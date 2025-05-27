from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
import datetime
import pendulum

from utils.company_utils import process_company_info_data, process_financial_data

with DAG(
    dag_id="company_financial_data_pipeline",
    schedule="50 14 * * Mon", # 毎週月曜日の14:50に実行 (市場データDAGの後に)
    start_date=pendulum.datetime(2025, 4, 10),
    catchup=False,
    tags=["DataLake", "DataWarehouse", "Company", "Financials"],
    template_searchpath='/home/airflow/airflow/airflow-dag/sqls'
) as dag:
    # 共通パラメータ (前週の月曜日と金曜日)
    today = datetime.date.today()
    common_params = {
        'prev_week_monday': today - datetime.timedelta(days=today.weekday() + 7),
        'prev_week_friday': today - datetime.timedelta(days=today.weekday() + 3),
    }

    # Task 1: 企業情報を取得しHDFSにアップロード
    get_and_upload_company_info_task = PythonOperator(
        task_id="get_and_upload_company_info",
        python_callable=process_company_info_data,
        op_kwargs={
            "hdfs_conn_id": "webhdfs_default",
            "market": "prime", # 対象市場を指定
        },
    )

    # Task 2: 財務諸表データを取得しHDFSにアップロード
    get_and_upload_financial_data_task = PythonOperator(
        task_id="get_and_upload_financial_data",
        python_callable=process_financial_data,
        op_kwargs={
            "hdfs_conn_id": "webhdfs_default",
            "market": "prime", # 対象市場を指定
        },
    )

    # Task 3: raw_financial_statements テーブルのパーティションを修復 (MSCK REPAIR TABLE)
    # raw_company_info はパーティションされていないため、MSCK REPAIRは不要
    msck_repair_financial_statements_task = SQLExecuteQueryOperator(
        task_id="msck_repair_raw_financial_statements",
        sql="MSCK REPAIR TABLE raw_financial_statements",
        conn_id="hiveserver2_default",
    )

    # Task 4: dim_company テーブルを更新 (upsert)
    upsert_dim_company_task = SQLExecuteQueryOperator(
        task_id="upsert_dim_company",
        sql="upsert_dim_company.sql",
        conn_id="hiveserver2_default",
        params=common_params # paramsはSQLファイル内で直接使用されないが、一貫性のため
    )

    # Task 5: fact_financials_annual テーブルを更新 (insert overwrite partition)
    load_fact_financials_annual_task = SQLExecuteQueryOperator(
        task_id="load_fact_financials_annual",
        sql="insert_fact_financials_annual.sql",
        conn_id="hiveserver2_default",
        params=common_params
    )

    # Task 6: fact_financials_quarterly テーブルを更新 (insert overwrite partition)
    load_fact_financials_quarterly_task = SQLExecuteQueryOperator(
        task_id="load_fact_financials_quarterly",
        sql="insert_fact_financials_quarterly.sql",
        conn_id="hiveserver2_default",
        params=common_params
    )

    # 依存関係の定義
    # データ取得とHDFSアップロードは並行
    [get_and_upload_company_info_task, get_and_upload_financial_data_task] >> \
    msck_repair_financial_statements_task # raw_company_infoはMSCK不要なので直接DWHロードへ

    # MSCK REPAIR後、DWHへのロード
    get_and_upload_company_info_task >> upsert_dim_company_task # 企業情報はMSCK不要なので直接DWHロードへ
    msck_repair_financial_statements_task >> [load_fact_financials_annual_task, load_fact_financials_quarterly_task]

    # このDAGは、dim_instrumentが更新された後に実行されることを想定しています。
    # そのため、etl_market_data_to_dwh_dag (14:40実行) の後にこのDAG (14:50実行) をスケジュールしています。
