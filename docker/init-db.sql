-- Wateen Database Initialization Script
-- This script initializes the database with the required user and extensions

-- Create the wateen_admin role if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT FROM pg_roles WHERE rolname = 'wateen_admin'
  ) THEN
    CREATE ROLE wateen_admin WITH LOGIN PASSWORD :'wateen_password';
    ALTER ROLE wateen_admin CREATEDB;
    ALTER ROLE wateen_admin CREATEROLE;
  END IF;
END $$;

-- Grant privileges on the database
GRANT ALL PRIVILEGES ON DATABASE wateen_db TO wateen_admin;

-- Connect to wateen_db to set up schema permissions
\c wateen_db

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO wateen_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO wateen_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO wateen_admin;

-- Create PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- Grant privileges on extensions
GRANT ALL PRIVILEGES ON SCHEMA public TO wateen_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wateen_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO wateen_admin;

-- Enable UUID extension for Django models
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
