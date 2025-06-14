# Автоматизация и оркестрация ML-пайплайна для диагностики заболевания

## Цель проекта
Разработать и автоматизировать ETL-процесс для построения модели машинного обучения, диагностирующей рак молочной железы, с использованием Apache Airflow и Python.

## Описание данных
- Источник: Breast Cancer Wisconsin Diagnostic Dataset
- Формат: CSV
- Ссылка: https://raw.githubusercontent.com/selva86/datasets/master/BreastCancer.csv
- Целевая переменная: Class (доброкачественная / злокачественная опухоль)

## Для начала работы
После копирования репозитория, создайте файл .env в корне проекта и заполните его в соотвествии с шаблоном:
```env
# Данные для PostgreSQL (используется Airflow)
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# Ключ для Web UI Airflow (замените на собственный)
AIRFLOW__WEBSERVER__SECRET_KEY=myultrasecretkey123

# Путь до JSON-файла сервисного аккаунта Google (для загрузки результатов)
GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/secrets/credentials.json

# ID папки Google Drive, куда выгружаются артефакты модели (замените на собственный)
GDRIVE_FOLDER_ID=1dN_kiXE90a94alksON24793773--plkad
```
Для тестирования/проверки etl-py-файлов можно использовать makefile-команды:
```
make install-requirements
```
Устанавливает необходимые зависимости в активную виртуальную среду (.venv, miniconda)

Далее можете воспользоваться командами для запуска кокретного скрипта:
```
make local-load
```
```
make local-preprocess
```
```
make local-train
```
```
make local-evaluate
```
```
make local-upload
```
Запуск всех скриптов:
```
make local-test-all
```

Сборка и запуск контейнеров (фоновый)
```
docker-compose up --build -d
```

Запуск контейнеров (фоновый)
```
make up
```
Доступ к web-интерфейсам (логин:пароль - admin:admin):
- Airflow Web UI: ```http://localhost:8080```
- Prometheus: ```http://localhost:3000```
- Grafana: ```http://localhost:3000```

Остановка и удаление контейнеров
```
make down
```

[Подробнее о makefile-командах](#makefile-команды)

##  Архитектура пайплайна


## Интеграция с хранилищем (Google Drive)

После завершения всех шагов пайплайна (train_model.py, evaluate.py) формируются:
- model.joblib — сериализованная модель (Logistic Regression)
- metrics.json — метрики качества (Accuracy, Precision, Recall, F1)

Они сохраняются в папке results/ (backup в upload/), а затем автоматически загружаются в облачное хранилище.

---

### Как реализована авторизация

Для безопасного доступа к Google Drive используется сервисный аккаунт, предоставляющий машинный доступ от имени проекта.
- drive_sa.json — ключ сервисного аккаунта (JSON), хранится в папке secrets/
- Авторизация происходит через библиотеку google-auth и google-api-python-client

---

### Необходимые переменные окружения
- GDRIVE_FOLDER_ID — ID папки на Google Drive, куда будет производиться выгрузка.
Пример: 1dN_kiXE90a94alksON24793773--plkad (предварительно для сервисного аккаунта необходимо предоставить доступ к папке)
- GOOGLE_APPLICATION_CREDENTIALS — абсолютный путь к файлу drive_sa.json.
Пример в .env:
GOOGLE_APPLICATION_CREDENTIALS="/opt/airflow/secrets/drive_sa.json"

---

### Как работает загрузка

Файл etl/upload_results.py использует функцию upload_to_storage(...), которая:
- Проверяет наличие файлов в results/
- Аутентифицируется через сервисный аккаунт
- Создаёт подпапку с меткой времени внутри GDRIVE_FOLDER_ID (например, 20250611_210512)
- Загружает в неё model.joblib и metrics.json
- Логирует результат с помощью utils/logger.py

### Результат
https://drive.google.com/drive/folders/1dN_kiXEhOI4ilksON24Azc7b3--pUlgH?usp=sharing
<img width="1440" alt="image" src="https://github.com/user-attachments/assets/81261a65-23f4-42da-9594-03c75508e449" />

---

## Prometheus
<img width="1719" alt="image" src="https://github.com/user-attachments/assets/e4da1917-8f11-495f-bb69-c0cde472be40" />

## Grafana
<img width="1728" alt="image" src="https://github.com/user-attachments/assets/b67f8fca-f34c-4a8a-963c-94b3ca5dba7d" />

## Airflow
<img width="1708" alt="image" src="https://github.com/user-attachments/assets/87f01f37-7857-4528-8aac-a6ba9b8d8d99" />
<img width="1294" alt="image" src="https://github.com/user-attachments/assets/4cafde7a-a59d-48b5-a396-cef08d8fe214" />
<img width="1707" alt="image" src="https://github.com/user-attachments/assets/455d4b14-8076-4df6-a781-080f13e356ee" />

## Makefile команды
### Установка зависимостей
```
make install-requirements
```
Устанавливает зависимости из test/requirements.txt. Используется для локального запуска скриптов вне Airflow. Зависимости устанавливаются в активную виртуальную среду (.venv, miniconda)

### Управление контейнерами
```
make up
```
Запускает все контейнеры Airflow (init, webserver, scheduler, triggerer, postgres) + Prometheus (statsd-exporter) + Grafana.

```
make down
```
Останавливает и удаляет все контейнеры.

### Просмотр логов
```
make logs
```
Показывает последние 100 строк логов всех сервисов.

```
make logs-webserver
make logs-scheduler
make logs-triggerer
```
Выводят логи отдельных сервисов Airflow: webserver, scheduler, triggerer.

### Локальное выполнение шагов пайплайна
Каждая команда запускает соответствующий скрипт без Airflow, напрямую из Python.
```
make local-load
```
Загружает датасет BreastCancer.csv из интернета и сохраняет в airflow/data/raw.csv.

```
make local-preprocess
```
Предобработка данных: удаление пропусков, масштабирование признаков, разбиение на train/test, сохранение в .joblib.

```
make local-train
```
Обучает модель LogisticRegression на подготовленных данных. Сохраняет модель в airflow/results/model.joblib.

```
make local-evaluate
```
Оценивает модель на тестовой выборке. Сохраняет метрики (Accuracy, Precision, Recall, F1) в airflow/results/metrics.json.

```
make local-upload
```
Загружает модель и метрики в Google Drive, используя drive_sa.json и GDRIVE_FOLDER_ID. Также сохраняет копии в airflow/uploaded.

```
make local-test-all
```
Полный прогон всех этапов пайплайна без Airflow:
- Загрузка данных
- Предобработка
- Обучение
- Оценка
- Выгрузка
