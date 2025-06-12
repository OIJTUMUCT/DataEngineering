from sklearn.linear_model import LogisticRegression
import joblib
import os

from utils.logger import get_logger

logger = get_logger("train_model")

def train_model():
    logger.info("Загрузка обучающих и тестовых данных...")
    X_train, X_test, y_train, y_test = joblib.load("data/split_data.joblib")

    logger.info("Инициализация и обучение модели LogisticRegression...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    os.makedirs("results", exist_ok=True)
    joblib.dump(model, "results/model.joblib")

    logger.info("Модель обучена и сохранена в results/model.joblib")