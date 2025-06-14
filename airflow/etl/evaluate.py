import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json
import argparse
import os

from utils.logger import get_logger

logger = get_logger("evaluate_model")


def evaluate_model(data_path="data/split_data.joblib", model_path="results/model.joblib", metrics_path="results/metrics.json"):
    logger.info("Загрузка данных из %s и модели из %s", data_path, model_path)

    try:
        X_train, X_test, y_train, y_test = joblib.load(data_path)
        model = joblib.load(model_path)
    except Exception as e:
        logger.exception("Ошибка при загрузке: %s", e)
        raise

    logger.info("Выполнение предсказания...")
    y_pred = model.predict(X_test)

    logger.info("Вычисление метрик...")
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
    }

    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    logger.info("Метрики сохранены в %s", metrics_path)
    for metric, value in metrics.items():
        logger.info(f"{metric}: {value:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Оценка модели по тестовым данным")
    parser.add_argument("--data_path", type=str, default="data/split_data.joblib", help="Путь к данным")
    parser.add_argument("--model_path", type=str, default="results/model.joblib", help="Путь к модели")
    parser.add_argument("--metrics_path", type=str, default="results/metrics.json", help="Куда сохранить метрики")

    args = parser.parse_args()
    evaluate_model(args.data_path, args.model_path, args.metrics_path)
