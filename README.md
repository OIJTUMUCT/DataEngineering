# Проект: Автоматизация и оркестрация ML-пайплайна для диагностики заболевания

## Цель проекта
Разработать и автоматизировать ETL-процесс для построения модели машинного обучения, диагностирующей рак молочной железы, с использованием Apache Airflow и Python.

## Описание данных
Источник: Breast Cancer Wisconsin Diagnostic Dataset
Формат: CSV
Ссылка: https://raw.githubusercontent.com/selva86/datasets/master/BreastCancer.csv
Целевая переменная: Class (доброкачественная / злокачественная опухоль)

##  Архитектура пайплайна


## Интеграция с хранилищем (Google Drive)

После завершения всех шагов пайплайна (train_model.py, evaluate.py) формируются:
- model.joblib — сериализованная модель (Logistic Regression)
- metrics.json — метрики качества (Accuracy, Precision, Recall, F1)

Они сохраняются в папке results/ (backup в upload/), а затем автоматически загружаются в облачное хранилище.

⸻

### Как реализована авторизация

Для безопасного доступа к Google Drive используется сервисный аккаунт, предоставляющий машинный доступ от имени проекта.
- drive_sa.json — ключ сервисного аккаунта (JSON), хранится в папке secrets/
- Авторизация происходит через библиотеку google-auth и google-api-python-client

⸻

### Необходимые переменные окружения
- GDRIVE_FOLDER_ID — ID папки на Google Drive, куда будет производиться выгрузка.
Пример: 1bn_ki67Eh904ilksON78Azc7b3--pYljk
- GOOGLE_APPLICATION_CREDENTIALS — абсолютный путь к файлу drive_sa.json.
Пример в .env:
GOOGLE_APPLICATION_CREDENTIALS="/opt/airflow/secrets/drive_sa.json"

⸻

### Как работает загрузка

Файл etl/upload_results.py использует функцию upload_to_storage(...), которая:
- Проверяет наличие файлов в results/
- Аутентифицируется через сервисный аккаунт
- Создаёт подпапку с меткой времени внутри GDRIVE_FOLDER_ID (например, 20250611_210512)
- Загружает в неё model.joblib и metrics.json
- Логирует результат с помощью utils/logger.py

⸻

## Prometeus
<img width="1719" alt="image" src="https://github.com/user-attachments/assets/e4da1917-8f11-495f-bb69-c0cde472be40" />

## Grafana
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/b67f8fca-f34c-4a8a-963c-94b3ca5dba7d" />

## Airflow
<img width="1708" alt="image" src="https://github.com/user-attachments/assets/87f01f37-7857-4528-8aac-a6ba9b8d8d99" />
<img width="1294" alt="image" src="https://github.com/user-attachments/assets/4cafde7a-a59d-48b5-a396-cef08d8fe214" />
<img width="1707" alt="image" src="https://github.com/user-attachments/assets/455d4b14-8076-4df6-a781-080f13e356ee" />



