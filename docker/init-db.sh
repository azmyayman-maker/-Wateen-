#!/bin/bash
# Wateen Database Initialization Script
set -e

# Read password from environment (Docker Compose injects POSTGRES_PASSWORD)
DB_PASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD environment variable is required}"

# Create the wateen_admin user and database if they don't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  -- Create wateen_admin role
  DO \$\$
  BEGIN
    IF NOT EXISTS (
      SELECT FROM pg_roles WHERE rolname = 'wateen_admin'
    ) THEN
      CREATE ROLE wateen_admin WITH LOGIN PASSWORD '${DB_PASSWORD}';
      ALTER ROLE wateen_admin CREATEDB;
      ALTER ROLE wateen_admin CREATEROLE;
    END IF;
  END
  \$\$;

  -- Grant privileges
  GRANT ALL PRIVILEGES ON DATABASE wateen_db TO wateen_admin;
  
  -- Connect to wateen_db
  \c wateen_db

  -- Set default privileges
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO wateen_admin;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO wateen_admin;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO wateen_admin;

  -- Create extensions
  CREATE EXTENSION IF NOT EXISTS postgis;
  CREATE EXTENSION IF NOT EXISTS postgis_topology;
  CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
  CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

  -- Grant permissions on schema
  GRANT ALL PRIVILEGES ON SCHEMA public TO wateen_admin;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wateen_admin;
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO wateen_admin;

EOSQL

echo "PostgreSQL initialization completed successfully!"
