import os
import shutil
import argparse
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils.logger import get_logger

logger = get_logger("upload")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def authenticate_drive(sa_path: str):
    credentials = service_account.Credentials.from_service_account_file(
        sa_path, scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials)

def timestamped_filename(filepath: str, timestamp: str):
    base, ext = os.path.splitext(os.path.basename(filepath))
    return f"{base}_{timestamp}{ext}"

def upload_file(service, filepath, drive_folder_id=None, timestamp=None):
    if timestamp:
        filename = timestamped_filename(filepath, timestamp)
    else:
        filename = os.path.basename(filepath)

    file_metadata = {"name": filename}
    if drive_folder_id:
        file_metadata["parents"] = [drive_folder_id]

    media = MediaFileUpload(filepath, resumable=True)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    logger.info(f"[upload_results] Файл {filename} загружен в Google Drive. ID: {uploaded.get('id')}")

def upload_to_storage(
    files=None,
    sa_path="secrets/drive_sa.json",
    drive_folder_id=None,
    backup_dir="uploaded",
    results_dir="results",
    timestamp=None
):
    if files is None:
        files = ["results/model.joblib", "results/metrics.json"]
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    logger.info(f"[upload_to_storage] Начинаем загрузку в Google Drive с таймстемпом: {timestamp}")
    service = authenticate_drive(sa_path)

    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    for f in files:
        if not os.path.exists(f):
            logger.warning("[upload_to_storage] Файл не найден: %s", f)
            continue

        # Отправка на Google Drive
        upload_file(service, f, drive_folder_id, timestamp)

        # Сохраняем в uploaded/
        new_name = timestamped_filename(f, timestamp)
        shutil.copy(f, os.path.join(backup_dir, os.path.basename(new_name)))

        # Сохраняем копию в results/
        shutil.copy(f, os.path.join(results_dir, os.path.basename(new_name)))

    logger.info(f"[upload_to_storage] Локальные копии файлов сохранены в {backup_dir}/ и {results_dir}/ с таймстемпом")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Загрузка артефактов в Google Drive и бэкап с версионированием")
    parser.add_argument("--sa_path", default="secrets/drive_sa.json", help="Путь к файлу сервисного аккаунта")
    parser.add_argument("--drive_folder_id", required=True, help="ID папки в Google Drive")
    parser.add_argument("--files", nargs="+", default=["results/model.joblib", "results/metrics.json"], help="Список файлов")
    parser.add_argument("--results_dir", default="results", help="Локальная папка для сохранения результатов")
    parser.add_argument("--backup_dir", default="uploaded", help="Локальная папка для копии")
    parser.add_argument("--timestamp", default=None, help="Формат времени (по умолчанию: YYYYMMDD_HHMMSS)")

    args = parser.parse_args()
    upload_to_storage(
        files=args.files,
        sa_path=args.sa_path,
        drive_folder_id=args.drive_folder_id,
        backup_dir=args.backup_dir,
        results_dir=args.results_dir,
        timestamp=args.timestamp
    )