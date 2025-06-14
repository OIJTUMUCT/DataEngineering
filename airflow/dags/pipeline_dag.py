from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import os

from etl.load_data import load_data
from etl.preprocess import preprocess_data
from etl.train_model import train_model
from etl.evaluate import evaluate_model
from etl.upload_results import upload_to_storage
from utils.logger import get_logger

logger = get_logger("pipeline_dag")

GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
if not GDRIVE_FOLDER_ID:
    logger.error("GDRIVE_FOLDER_ID не установлен в переменных окружения!")
    raise ValueError("GDRIVE_FOLDER_ID отсутствует!")

def airflow_upload():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_to_storage(
        drive_folder_id=GDRIVE_FOLDER_ID,
        timestamp=timestamp,
    )

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

    task_load = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
        retries=3,
        retry_delay=timedelta(minutes=2),
        execution_timeout=timedelta(seconds=30),
        depends_on_past=False,
    )

    task_preprocess = PythonOperator(
        task_id="preprocess_data",
        python_callable=preprocess_data,
        depends_on_past=True,
    )

    task_train = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
        retries=1,
        execution_timeout=timedelta(minutes=10),
        depends_on_past=True,
    )

    task_evaluate = PythonOperator(
        task_id="evaluate_model",
        python_callable=evaluate_model,
        depends_on_past=True,
    )

    task_upload = PythonOperator(
        task_id="upload_results",
        python_callable=airflow_upload,
        retries=2,
        retry_delay=timedelta(minutes=3),
        execution_timeout=timedelta(minutes=5),
        depends_on_past=True,
    )

    success_end = EmptyOperator(task_id="success_end", trigger_rule=TriggerRule.ALL_SUCCESS)
    failure_end = EmptyOperator(task_id="failure_end", trigger_rule=TriggerRule.ONE_FAILED)

    start >> task_load >> task_preprocess >> task_train >> task_evaluate >> task_upload

    [task_upload] >> success_end
    [task_load, task_preprocess, task_train, task_evaluate, task_upload] >> failure_end