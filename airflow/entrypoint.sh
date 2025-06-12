#!/bin/bash
set -e

echo "Ожидание PostgreSQL на порту 5432..."
until nc -z postgres 5432; do
  echo "PostgreSQL ещё не доступен, ожидание..."
  sleep 2
done
echo "PostgreSQL доступен"

echo "Инициализация БД..."
airflow db migrate

echo "Проверка/создание пользователя admin..."
if ! airflow users list | grep -q '^admin\s'; then
  airflow users create \
    --username admin \
    --password admin \
    --firstname Anonymous \
    --lastname X \
    --role Admin \
    --email admin@example.com
else
  echo "Пользователь admin уже существует"
fi

DAG_ID="medical_etl_pipeline"

echo "Ожидание загрузки DAG: $DAG_ID..."
until airflow dags list | grep -q "$DAG_ID"; do
  echo "DAG '$DAG_ID' ещё не найден, ожидание..."
  sleep 5
done

echo "Список DAG'ов:"
airflow dags list

echo "Безопасная разблокировка DAG-ов (через Python)..."
airflow dags list --output json | python3 -c '
import sys, json, subprocess
dags = json.load(sys.stdin)
for dag in dags:
    dag_id = dag["dag_id"]
    try:
        subprocess.run(["airflow", "dags", "show", dag_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"Разблокировка {dag_id}")
        subprocess.run(["airflow", "dags", "unpause", dag_id], check=True)
    except subprocess.CalledProcessError:
        print(f"Пропуск {dag_id} (не загружен)")
'

echo "Инициализация завершена"