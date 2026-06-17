# Runbook — Demo Delivery Pipeline (Airflow + Docker)

## Requisitos previos

| Requisito       | Versión   | Cómo verificar              |
|-----------------|-----------|-----------------------------|
| Docker Desktop  | ≥ 4.x     | `docker --version`          |
| Docker Compose  | ≥ 2.x     | `docker-compose version`    |
| RAM libre       | ≥ 4 GB    | Docker Desktop → Resources  |
| Puerto 8080     | Disponible | `lsof -i :8080`            |

---

## Levantar el stack

```bash
chmod +x run_airflow.sh
./run_airflow.sh
```

El script construye la imagen, inicia los servicios y espera a que el webserver
esté disponible. La primera vez tarda ~3 min (descarga de imagen base).

---

## Acceder a la UI

```
URL:         http://localhost:8080
Usuario:     admin
Contraseña:  admin
```

---

## Ejecutar el pipeline

### Desde la UI

1. Abrir `http://localhost:8080` e iniciar sesión.
2. Hacer clic en **delivery_delay_pipeline**.
3. Presionar **▶ Trigger DAG** (arriba a la derecha).
4. Ir a la vista **Graph** y observar las tareas ponerse en verde una por una.
5. Clic en cualquier tarea → **Log** para ver su salida.

### Desde la terminal

```bash
docker-compose exec airflow-scheduler airflow dags trigger delivery_delay_pipeline
docker-compose exec airflow-scheduler airflow dags list-runs -d delivery_delay_pipeline
```

---

## Demo: simulación de fallo en cascada

Demuestra por qué un orquestador es mejor que un script.
Cuando `clean` falla, Airflow bloquea **automáticamente** todas las tareas siguientes.

```bash
# 1. Activar el interruptor de fallo
docker-compose exec airflow-scheduler airflow variables set FAIL_CLEAN true

# 2. Disparar el DAG desde la UI
#    → clean falla en rojo
#    → engineer, train, evaluate, generate quedan en upstream_failed

# 3. Recuperar
docker-compose exec airflow-scheduler airflow variables set FAIL_CLEAN false
```

---

## Uso diario

| Acción                        | Comando                          |
|-------------------------------|----------------------------------|
| Levantar el stack             | `./run_airflow.sh`               |
| Apagar el stack               | `docker-compose down`            |
| Ver logs de un servicio       | `docker-compose logs -f airflow-scheduler` |
| Reconstruir tras un cambio    | `docker-compose up -d --build`   |

---

## Archivos de salida

Después de una ejecución exitosa:

```
data/processed/
├── X_train.csv
├── X_test.csv
├── y_train.csv
└── y_test.csv
```

---

## Solución de problemas

**Puerto 8080 en uso**
```bash
lsof -i :8080
kill -9 <PID>
```

**El DAG no aparece en la UI**
```bash
docker-compose exec airflow-scheduler airflow dags list-import-errors
```

**Reseteo completo**
```bash
docker-compose down -v
./run_airflow.sh
```
