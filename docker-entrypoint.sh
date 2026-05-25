#!/bin/sh
set -eu

sed -i "s/^ssl = on/ssl = off/" /etc/postgresql/17/main/postgresql.conf
service postgresql start

su postgres -c "psql -v ON_ERROR_STOP=1 -c \"ALTER USER postgres WITH PASSWORD 'postgres';\""
su postgres -c "psql -v ON_ERROR_STOP=1 -tc \"SELECT 1 FROM pg_database WHERE datname='aa_db'\" | grep -q 1 || psql -v ON_ERROR_STOP=1 -c \"CREATE DATABASE aa_db;\""

python src/manage.py migrate --noinput
python src/manage.py collectstatic --noinput
python src/manage.py runserver 0.0.0.0:8000
