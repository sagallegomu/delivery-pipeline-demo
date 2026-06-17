# Pipeline de Predicción de Retrasos en Entregas

Demo práctica de 15 minutos para la clase de **ingeniería de datos**.
Construimos un pipeline de ML para predecir si una orden de e-commerce llegará tarde,
y lo orquestamos con Apache Airflow.

## ¿Qué hay en este repo?

```
notebooks/delivery_pipeline_demo.ipynb   # La clase: pipeline paso a paso en Python
dags/pipeline.py                         # Las 6 funciones del pipeline (importadas por el DAG)
dags/delivery_pipeline_dag.py            # El mismo pipeline como DAG de Airflow
data/raw/orders.csv                      # Dataset sintético: 1,200 órdenes de e-commerce
docker-compose.yml                       # Stack de Airflow (postgres + webserver + scheduler)
run_airflow.sh                           # Script para levantar el stack
runbook.md                               # Instrucciones de operación y demo de fallo
```

## Levantar Airflow

```bash
chmod +x run_airflow.sh
./run_airflow.sh
```

UI disponible en `http://localhost:8080` — usuario `admin` / contraseña `admin`.

Ver `runbook.md` para instrucciones completas y la demo del fallo simulado.

## Stack

- Python 3.12 · pandas · scikit-learn · Apache Airflow 2.9.3
- Docker Compose (LocalExecutor + Postgres)
