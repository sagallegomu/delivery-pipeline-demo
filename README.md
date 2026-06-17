# Delivery Delay Pipeline

Pipeline de ML que predice si una orden de e-commerce llegará tarde, orquestado con Apache Airflow. Construido como demo práctica de 15 minutos para la clase de ingeniería de datos.

## ¿Qué hace este proyecto?

Toma 1,200 órdenes sintéticas de e-commerce y entrena un clasificador que predice retrasos en entregas. El mismo código corre primero como un script en un notebook, y luego como un DAG de Airflow — mostrando por qué un orquestador es necesario en producción.

## Estructura

```
delivery-pipeline-demo/
├── dags/
│   ├── pipeline.py                  # Las 6 funciones del pipeline (Python puro)
│   └── delivery_pipeline_dag.py     # El mismo pipeline como DAG de Airflow
├── data/
│   └── raw/
│       └── orders.csv               # Dataset sintético: 1,200 órdenes
├── notebooks/
│   └── delivery_pipeline_demo.ipynb # Demo paso a paso del pipeline
├── Dockerfile                       # Imagen de Airflow con pandas + scikit-learn
├── docker-compose.yml               # Stack completo: Airflow + Postgres
├── run_airflow.sh                   # Script para levantar el stack
├── pyproject.toml                   # Dependencias gestionadas con Poetry
└── runbook.md                       # Guía de operación y demo de fallo
```

## El pipeline

```
extract → clean → engineer → train → evaluate → generate
```

| Task | Qué hace |
|------|----------|
| `extract` | Lee `orders.csv` — 1,200 órdenes con categoría, estado, valor |
| `clean` | Rellena ~75 nulos en `order_value` y `freight_value` con la mediana |
| `engineer` | Crea `same_state`, `day_of_week`, `is_weekend`; encodea categóricas |
| `train` | RandomForest 100 árboles, split 80/20 estratificado |
| `evaluate` | `classification_report` — precision, recall, F1 por clase |
| `generate` | Top 20 órdenes con mayor probabilidad de retraso |

## Setup

### Requisitos

- Docker con Compose (`docker-compose version`)
- Python 3.12 + Poetry (solo para desarrollo local)

### Levantar Airflow

```bash
chmod +x run_airflow.sh
./run_airflow.sh
```

UI en `http://localhost:8080` — usuario `admin` / contraseña `admin`.

### Desarrollo local (notebook)

```bash
poetry install
poetry run jupyter lab
```

Seleccionar el kernel **Python 3.12 (demo-henry)** en el notebook.

## Demo de fallo en cascada

La característica más pedagógica: muestra por qué Airflow es mejor que un script.

```bash
# Activar fallo simulado en la tarea clean
docker-compose exec airflow-scheduler airflow variables set FAIL_CLEAN true

# Disparar el DAG desde la UI → clean falla → engineer/train/evaluate/generate
# quedan en upstream_failed. Airflow no entrena con datos sucios.

# Recuperar
docker-compose exec airflow-scheduler airflow variables set FAIL_CLEAN false
```

## Stack

| Tecnología | Versión | Rol |
|------------|---------|-----|
| Apache Airflow | 2.9.3 | Orquestador |
| Python | 3.12 | Runtime |
| pandas | 2.2.2 | Manipulación de datos |
| scikit-learn | 1.5.0 | Modelo ML (RandomForest) |
| PostgreSQL | 13 | Metadata de Airflow |
| Poetry | 1.8.5 | Gestión de dependencias |
| Docker Compose | 2.x | Infraestructura local |
