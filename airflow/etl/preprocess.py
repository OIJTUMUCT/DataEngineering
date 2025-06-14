import pandas as pd
import numpy as np
import os
import argparse
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check
from utils.logger import get_logger

logger = get_logger(__name__)

schema = DataFrameSchema({
    "Cl.thickness": Column(int, Check.in_range(1, 10), nullable=False),
    "Cell.size": Column(int, Check.in_range(1, 10), nullable=False),
    "Cell.shape": Column(int, Check.in_range(1, 10), nullable=False),
    "Marg.adhesion": Column(int, Check.in_range(1, 10), nullable=False),
    "Epith.c.size": Column(int, Check.in_range(1, 10), nullable=False),
    "Bare.nuclei": Column(float, Check.in_range(1, 10), nullable=False),
    "Bl.cromatin": Column(int, Check.in_range(1, 10), nullable=False),
    "Normal.nucleoli": Column(int, Check.in_range(1, 10), nullable=False),
    "Mitoses": Column(int, Check.in_range(0, 10), nullable=False),
    "Class": Column(int, Check.isin([0, 1]), nullable=False),
})

def preprocess_data(data_dir="/opt/airflow/data"):
    raw_path = os.path.join(data_dir, "raw.csv")
    split_path = os.path.join(data_dir, "split_data.joblib")
    scaler_path = os.path.join(data_dir, "scaler.joblib")

    if not os.path.exists(raw_path):
        logger.error("Файл не найден: %s", raw_path)
        raise FileNotFoundError(f"raw.csv отсутствует по пути {raw_path}")

    df = pd.read_csv(raw_path, na_values=["NA", "?", "NaN", "Nan", "nan"])

    null_rows = df.isnull().any(axis=1).sum()
    if null_rows:
        logger.warning("Удалено строк с пропущенными значениями: %d", null_rows)
    df.dropna(inplace=True)

    df.drop(columns=["Id"], errors='ignore', inplace=True)

    # Валидация по схеме
    try:
        df = schema.validate(df)
    except pa.errors.SchemaError as e:
        logger.error("Ошибка схемы Pandera: %s", e)
        raise

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
    logger.info("  > %s", split_path)
    logger.info("  > %s", scaler_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Предобработка данных")
    parser.add_argument("--data_dir", type=str, default="/opt/airflow/data",
                        help="Каталог, содержащий raw.csv и сохраняющий результаты")
    args = parser.parse_args()

    preprocess_data(args.data_dir)