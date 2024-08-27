#!/bin/bash
set -e

export PGPASSWORD="$POSTGRES_PASSWORD"

# Создание базы данных и добавление расширения PostGIS
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --host "$POSTGRES_HOST" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS postgis_topology;
EOSQL
unset PGPASSWORD
