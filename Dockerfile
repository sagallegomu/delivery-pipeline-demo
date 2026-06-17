FROM apache/airflow:2.9.3-python3.12

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

USER airflow
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry==1.8.5 \
    && poetry export --without-hashes --only main -f requirements.txt -o /tmp/requirements.txt \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip uninstall -y poetry \
    && rm /tmp/requirements.txt
