import os
import shutil
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils.logger import get_logger

logger = get_logger("upload")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
SERVICE_ACCOUNT_FILE = "secrets/drive_sa.json"  # этот файл ты скачал ранее
GDRIVE_FOLDER_ID = "1dN_kiXEhOI4ilksON24Azc7b3--pUlgH"  # получи из URL папки Drive

def authenticate_drive():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials)

def upload_file(service, filepath, drive_folder_id=None):
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

def upload_to_storage():
    logger.info("[upload_to_storage] Начинаем загрузку в Google Drive...")
    service = authenticate_drive()
    files = ["results/model.joblib", "results/metrics.json"]

    for f in files:
        upload_file(service, f, GDRIVE_FOLDER_ID)

    os.makedirs("uploaded", exist_ok=True)
    for f in files:
        shutil.copy(f, os.path.join("uploaded", os.path.basename(f)))
    logger.info("[upload_to_storage] Локальная копия файлов сохранена в uploaded/")