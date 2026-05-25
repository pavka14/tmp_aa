FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY src/requirements.txt ./src/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r ./src/requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python src/manage.py migrate --noinput && python src/manage.py collectstatic --noinput && python src/manage.py runserver 0.0.0.0:8000"]
