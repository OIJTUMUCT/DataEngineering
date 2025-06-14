include .env
export

PYTHON=docker-compose exec airflow-webserver python3
LOCAL_PYTHON=$(shell which python)

DATA=airflow/data/raw.csv
SPLIT=airflow/data/split_data.joblib
MODEL=airflow/results/model.joblib
METRICS=airflow/results/metrics.json

up:
	docker-compose up -d
	@echo "Контейнеры запущены"

down:
	docker-compose down
	@echo "Контейнеры остановлены"

logs:
	docker-compose logs --tail=100 -f

logs-scheduler:
	docker-compose logs -f airflow-scheduler

logs-webserver:
	docker-compose logs -f airflow-webserver

logs-triggerer:
	docker-compose logs -f airflow-triggerer

local-load:
	PYTHONPATH=airflow python airflow/etl/load_data.py --url=https://raw.githubusercontent.com/selva86/datasets/master/BreastCancer.csv --save_path=airflow/data/raw.csv

local-preprocess:
	PYTHONPATH=airflow python airflow/etl/preprocess.py --data_dir=airflow/data

local-train:
	PYTHONPATH=airflow python airflow/etl/train_model.py --data_path=$(SPLIT) --output_path=$(MODEL)

local-evaluate:
	PYTHONPATH=airflow \
	python airflow/etl/evaluate.py \
		--data_path=airflow/data/split_data.joblib \
		--model_path=airflow/results/model.joblib \
		--metrics_path=airflow/results/metrics.json

local-upload:
	PYTHONPATH=airflow \
	python airflow/etl/upload_results.py \
		--sa_path=secrets/drive_sa.json \
		--drive_folder_id=$(GDRIVE_FOLDER_ID) \
		--files airflow/results/model.joblib airflow/results/metrics.json \
		--backup_dir=airflow/uploaded \
		--results_dir=airflow/results


local-test-all: local-load local-preprocess local-train local-evaluate local-upload

install-requirements:
	@pip install -r test/requirements.txt