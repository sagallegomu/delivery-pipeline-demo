"""Lógica del pipeline de predicción de retrasos en entregas.

Seis funciones Python puras — sin Airflow. El DAG las importa y las envuelve
como tasks. El notebook las ejecuta paso a paso para la demo de la clase.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "raw" / "orders.csv"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

CATEGORICAL_FEATURES = ["product_category", "seller_state", "customer_state"]
NUMERIC_FEATURES = [
    "order_value", "freight_value", "estimated_days",
    "day_of_week", "same_state", "is_weekend",
]
TARGET = "is_late"


def extract_data() -> pd.DataFrame:
    """Paso 1 — Lee las órdenes desde la fuente de datos."""
    df = pd.read_csv(DATA_PATH, parse_dates=["purchase_date"])
    print(f"✅ extract | {len(df):,} órdenes | {df.shape[1]} columnas")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Paso 2 — Corrige tipos y rellena nulos."""
    df = df.copy()
    before = len(df)
    df = df.dropna(subset=["product_category", "seller_state", "customer_state"])
    df["order_value"] = pd.to_numeric(df["order_value"], errors="coerce")
    df["freight_value"] = pd.to_numeric(df["freight_value"], errors="coerce")
    df["order_value"] = df["order_value"].fillna(df["order_value"].median())
    df["freight_value"] = df["freight_value"].fillna(df["freight_value"].median())
    print(f"✅ clean | {before} → {len(df)} órdenes | nulos: {df.isnull().sum().sum()}")
    return df


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Paso 3 — Crea features derivadas y encodea categóricas."""
    df = df.copy()
    df["same_state"] = (df["seller_state"] == df["customer_state"]).astype(int)
    df["day_of_week"] = df["purchase_date"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    le = LabelEncoder()
    for col in CATEGORICAL_FEATURES:
        df[col] = le.fit_transform(df[col].astype(str))
    features = CATEGORICAL_FEATURES + NUMERIC_FEATURES + [TARGET]
    df_model = df[features]
    print(f"✅ engineer | {len(CATEGORICAL_FEATURES)} features encodadas | shape: {df_model.shape}")
    return df_model


def train_model(df: pd.DataFrame):
    """Paso 4 — Entrena el clasificador y persiste los splits."""
    X = df.drop(columns=[TARGET])
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    X_train.to_csv(PROCESSED_DIR / "X_train.csv", index=True)
    X_test.to_csv(PROCESSED_DIR / "X_test.csv", index=True)
    y_train.to_csv(PROCESSED_DIR / "y_train.csv", index=True)
    y_test.to_csv(PROCESSED_DIR / "y_test.csv", index=True)
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    print(f"✅ train | {len(X_train):,} entrenamiento | {len(X_test):,} prueba")
    print(f"   💾 splits guardados en {PROCESSED_DIR}/")
    return model, X_test, y_test


def evaluate_model(model, X_test: pd.DataFrame, y_test) -> None:
    """Paso 5 — Métricas de desempeño sobre el set de prueba."""
    y_pred = model.predict(X_test)
    # XCom puede cambiar el dtype al serializar — forzamos int para sklearn
    y_true = pd.Series(y_test).astype(int).values
    print("✅ evaluate\n")
    print(classification_report(y_true, y_pred, target_names=["A tiempo", "Tarde"]))


def generate_predictions(
    model, X_test: pd.DataFrame, df_original: pd.DataFrame, top_n: int = 20
) -> pd.DataFrame:
    """Paso 6 — Top N órdenes con mayor probabilidad de llegar tarde."""
    probs = model.predict_proba(X_test)[:, 1]
    result = df_original.loc[
        X_test.index,
        ["order_id", "product_category", "seller_state", "customer_state", "order_value"],
    ].copy()
    result["delay_probability"] = probs
    result = result.sort_values("delay_probability", ascending=False).head(top_n)
    result["delay_probability"] = result["delay_probability"].map("{:.1%}".format)
    print("✅ generate | Top órdenes con mayor riesgo de retraso:")
    print(result.to_string())
    return result.reset_index(drop=True)
