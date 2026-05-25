FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql ssl-cert \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt ./src/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r ./src/requirements.txt

COPY . .

EXPOSE 8000

CMD ["./docker-entrypoint.sh"]
