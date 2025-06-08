import pendulum

from airflow.models.dag import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# DAG定義
with DAG(
    dag_id='elt_data_to_dwh_dag',
    description='ELT DAG to load data from Raw Zone to DWH (Fact/Dimension)',
    schedule='00 13 * * Mon',
    start_date=pendulum.datetime(2025, 4, 10),
    catchup=False, # 過去分の実行をスキップ
    tags=['DataWarehouse', 'Company', 'Stock', 'Forex', 'Index'],
    template_searchpath='/home/airflow/airflow/airflow-dag/include/sql'
) as dag:


    # --- Dimension 更新タスク ---

    upsert_dim_date = SQLExecuteQueryOperator(
        task_id='upsert_dim_date',
        sql='upsert_dim_date.sql',
        conn_id="hiveserver2_default",
    )
    upsert_dim_company = SQLExecuteQueryOperator(
        task_id='upsert_dim_company',
        sql='upsert_dim_company.sql',
        conn_id="hiveserver2_default",
    )
    upsert_dim_currency = SQLExecuteQueryOperator(
        task_id='upsert_dim_currency',
        sql='upsert_dim_currency.sql',
        conn_id="hiveserver2_default",
    )
    upsert_dim_index = SQLExecuteQueryOperator(
        task_id='upsert_dim_index',
        sql='upsert_dim_index.sql',
        conn_id="hiveserver2_default",
    )

    # --- Fact 更新タスク ---

    insert_fact_company = SQLExecuteQueryOperator(
        task_id='load_fact_company',
        sql='insert_fact_company_financials.sql',
        conn_id="hiveserver2_default",
    )
    insert_fact_stock = SQLExecuteQueryOperator(
        task_id='load_fact_stock',
        sql='insert_fact_stock.sql',
        conn_id="hiveserver2_default",
    )
    insert_fact_forex = SQLExecuteQueryOperator(
        task_id='load_fact_forex',
        sql='insert_fact_forex.sql',
        conn_id="hiveserver2_default",
    )
    insert_fact_index = SQLExecuteQueryOperator(
        task_id='load_fact_index',
        sql='insert_fact_index.sql',
        conn_id="hiveserver2_default",
    )

    # --- タスク依存関係 ---
    dimensions_updated = [upsert_dim_date, upsert_dim_company, upsert_dim_currency, upsert_dim_index]
    dimensions_updated >> insert_fact_company
    dimensions_updated >> insert_fact_stock
    dimensions_updated >> insert_fact_forex
    dimensions_updated >> insert_fact_index
