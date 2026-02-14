#!/bin/bash

# if any of the commands in your code fails, the whole script fails
set -o errexit
# fail if any of your variables is not set
set -o nounset

postgres_ready() {
    nc -z $DB_HOST $DB_PORT
}

# Wait for Postgres to be available
echo "Waiting for postgres..."
until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
echo "Postgres is up - continuing..."

exec "$@"
