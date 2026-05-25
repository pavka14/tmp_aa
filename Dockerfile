FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

COPY src/requirements.txt ./src/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r ./src/requirements.txt

FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql ssl-cert \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src/requirements.txt ./src/requirements.txt
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --no-index --find-links=/wheels -r ./src/requirements.txt

COPY . .

EXPOSE 8000

CMD ["./docker-entrypoint.sh"]
