#!/usr/bin/env bash
set -euo pipefail

echo "🚀  Levantando stack de Airflow..."

mkdir -p logs data/processed
export AIRFLOW_UID=$(id -u)

docker compose up -d --build

echo "⏳  Esperando a que el webserver esté disponible..."
until curl -sf http://localhost:8080/health | grep -q '"healthy"'; do
    printf '.'
    sleep 3
done

printf '\n\n'
echo "✅  Airflow listo"
echo "    URL:         http://localhost:8080"
echo "    Usuario:     admin"
echo "    Contraseña:  admin"
