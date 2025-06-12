from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta

from etl.load_data import load_data
from etl.preprocess import preprocess_data
from etl.train_model import train_model
from etl.evaluate import evaluate_model
from etl.upload_results import upload_to_storage

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="medical_etl_pipeline",
    start_date=datetime(2025, 6, 11),
    schedule_interval="@once",
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    tags=["ml", "medical", "airflow"],
    description="ETL-пайплайн предиктивной модели для диагностики рака молочной железы",
) as dag:

    start = EmptyOperator(task_id="start")

    task_load = PythonOperator(task_id="load_data", python_callable=load_data, depends_on_past=True)
    task_preprocess = PythonOperator(task_id="preprocess_data", python_callable=preprocess_data, depends_on_past=True)
    task_train = PythonOperator(task_id="train_model", python_callable=train_model, depends_on_past=True)
    task_evaluate = PythonOperator(task_id="evaluate_model", python_callable=evaluate_model, depends_on_past=True)
    task_upload = PythonOperator(task_id="upload_results", python_callable=upload_to_storage, depends_on_past=True)

    success_end = EmptyOperator(task_id="success_end", trigger_rule=TriggerRule.ALL_SUCCESS)
    failure_end = EmptyOperator(task_id="failure_end", trigger_rule=TriggerRule.ONE_FAILED)

    # Основной поток
    start >> task_load >> task_preprocess >> task_train >> task_evaluate >> task_upload

    # Финальные точки: зависят от task_upload, но должны учитывать все upstream
    [task_upload] >> success_end
    [task_load, task_preprocess, task_train, task_evaluate, task_upload] >> failure_end