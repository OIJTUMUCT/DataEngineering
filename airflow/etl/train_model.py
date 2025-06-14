from sklearn.linear_model import LogisticRegression
import joblib
import os
import argparse

from utils.logger import get_logger

logger = get_logger("train_model")

def train_model(data_path="data/split_data.joblib", output_path="results/model.joblib"):
    logger.info("Загрузка обучающих и тестовых данных из %s...", data_path)

    try:
        X_train, X_test, y_train, y_test = joblib.load(data_path)
    except Exception as e:
        logger.exception("Ошибка при загрузке данных: %s", e)
        raise

    logger.info("Инициализация и обучение модели LogisticRegression...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(model, output_path)

    logger.info("Модель обучена и сохранена в %s", output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обучение модели LogisticRegression")
    parser.add_argument("--data_path", type=str, default="data/split_data.joblib",
                        help="Путь к файлу с предобработанными данными")
    parser.add_argument("--output_path", type=str, default="results/model.joblib",
                        help="Путь для сохранения модели")

    args = parser.parse_args()
    train_model(args.data_path, args.output_path)