import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from utils.logger import get_logger

logger = get_logger(__name__)

def preprocess_data():
    data_dir = "/opt/airflow/data"
    raw_path = os.path.join(data_dir, "raw.csv")
    split_path = os.path.join(data_dir, "split_data.joblib")
    scaler_path = os.path.join(data_dir, "scaler.joblib")

    if not os.path.exists(raw_path):
        logger.error("Файл не найден: %s", raw_path)
        raise FileNotFoundError(f"raw.csv отсутствует по пути {raw_path}")

    # Учитываем 'NA' как пропуски
    df = pd.read_csv(raw_path, na_values=["NA"])

    # Удаление строк с отсутствующими значениями (в т.ч. из-за NA)
    null_rows = df.isnull().any(axis=1).sum()
    if null_rows:
        logger.warning("Удалено строк с пропущенными значениями: %d", null_rows)
    df.dropna(inplace=True)

    df.drop(columns=["Id"], errors='ignore', inplace=True)

    X = df.drop("Class", axis=1)
    y = df["Class"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    os.makedirs(data_dir, exist_ok=True)
    joblib.dump((X_train, X_test, y_train, y_test), split_path)
    joblib.dump(scaler, scaler_path)

    logger.info("Данные предобработаны и сохранены:")
    logger.info("  ➤ %s", split_path)
    logger.info("  ➤ %s", scaler_path)