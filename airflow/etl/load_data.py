import pandas as pd
import os
import argparse
from utils.logger import get_logger

logger = get_logger(__name__)

def load_data(url="https://raw.githubusercontent.com/selva86/datasets/master/BreastCancer.csv", save_path="/opt/airflow/data/raw.csv"):

    if os.path.exists(save_path):
        logger.info("Файл уже существует: %s — загрузка пропущена.", save_path)
        return

    try:
        logger.info("Начинается загрузка данных с %s", url)
        df = pd.read_csv(url)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)

        logger.info("Данные успешно сохранены в %s", save_path)
    except Exception as e:
        logger.exception("Ошибка при загрузке данных: %s", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Загрузка датасета")
    parser.add_argument("--url", type=str, default="https://raw.githubusercontent.com/selva86/datasets/master/BreastCancer.csv",
                        help="URL скачивания датасета")
    parser.add_argument("--save_path", type=str, default="/opt/airflow/data/raw.csv",
                        help="Путь для сохранения CSV-файла")
    args = parser.parse_args()

    load_data(args.url, args.save_path)