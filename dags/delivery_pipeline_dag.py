"""DAG de Airflow — el pipeline del notebook, ahora orquestado.

Las mismas seis funciones de ``pipeline.py`` se convierten en seis tasks.
Airflow agrega lo que un script no puede: schedule diario, reintentos automáticos,
logs por tarea, y un grafo de dependencias que bloquea pasos siguientes
cuando uno anterior falla.

Demo de fallo
-------------
Establecer la Variable ``FAIL_CLEAN`` en ``"true"`` hace que la tarea ``clean``
falle a propósito. Las tareas siguientes pasan a *upstream_failed* — Airflow
no entrena un modelo con datos que nunca fueron limpiados.

    docker compose exec airflow-scheduler airflow variables set FAIL_CLEAN true
    docker compose exec airflow-scheduler airflow variables set FAIL_CLEAN false
"""

from __future__ import annotations

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable

import pipeline

default_args = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": pendulum.duration(minutes=1),
}


@dag(
    dag_id="delivery_delay_pipeline",
    description="Pipeline diario: predice qué órdenes llegarán tarde",
    schedule="0 6 * * *",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    default_args=default_args,
    tags=["ml", "delivery", "demo"],
)
def delivery_delay_pipeline():

    @task
    def extract():
        return pipeline.extract_data()

    @task
    def clean(df):
        if Variable.get("FAIL_CLEAN", default_var="false").lower() == "true":
            raise ValueError(
                "💥 Fallo simulado en clean — las tareas siguientes quedarán bloqueadas."
            )
        return pipeline.clean_data(df)

    @task
    def engineer(df):
        return pipeline.feature_engineering(df)

    @task
    def train(df_features):
        model, X_test, y_test = pipeline.train_model(df_features)
        return {"model": model, "X_test": X_test, "y_test": y_test}

    @task
    def evaluate(trained):
        pipeline.evaluate_model(trained["model"], trained["X_test"], trained["y_test"])

    @task
    def generate(trained, df_clean):
        predictions = pipeline.generate_predictions(
            trained["model"], trained["X_test"], df_clean
        )
        print("\n📋 Órdenes en riesgo — notificar al equipo de operaciones:")
        print(predictions.to_string())
        return predictions

    # ── Grafo de dependencias ──────────────────────────────────────────────────
    raw      = extract()
    clean_df = clean(raw)
    features = engineer(clean_df)
    trained  = train(features)

    evaluate(trained)
    generate(trained, clean_df)   # necesita el modelo Y los datos limpios (order_id, etc.)


delivery_delay_pipeline()
