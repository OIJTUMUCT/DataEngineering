# etl/evaluate.py
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json

from utils.logger import get_logger  # предполагается, что logger лежит в utils/logger.py

logger = get_logger("evaluate_model")


def evaluate_model():
    logger.info("Загрузка данных и модели...")
    X_train, X_test, y_train, y_test = joblib.load("data/split_data.joblib")
    model = joblib.load("results/model.joblib")

    logger.info("Выполнение предсказания...")
    y_pred = model.predict(X_test)

    logger.info("Вычисление метрик...")
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
    }

    with open("results/metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)

    logger.info("Метрики сохранены в results/metrics.json")
    for metric, value in metrics.items():
        logger.info(f"{metric}: {value:.4f}")
